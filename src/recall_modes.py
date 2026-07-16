"""Progressive-disclosure response modes for memory_recall.

Two transforms on top of the standard ``Recall.search`` result:

* :func:`index_response` — strip every item to an ultra-compact set of
  metadata fields (id + title + score + type + project + created_at). No
  content, no context, no cognitive expansion. ~40-60 tokens per hit.
* :func:`timeline_response` — flatten grouped hits into a chronological
  list and pad each hit with ±N neighbours from the same session so the
  caller can see what happened around the match.

Designed for a 3-layer workflow: ``recall(mode='index')`` → pick ids →
``memory_get(ids=[...])`` for full content, saving 80-90 %% of the tokens
versus ``detail='full'`` on the same ``limit``.
"""

from __future__ import annotations

import json
import re
from typing import Any


# ── index mode ────────────────────────────────────────────────

_TITLE_MAX = 80
_RAG_SUMMARY_MAX = 220
_RAG_DEDUPE_MAX = 180
_RECALL_DIAGNOSTIC_KEYS = (
    "graph_expand_applied",
    "graph_expand_reason",
    "graph_expand_families",
    "routed_via",
    "routed_graph_families",
    "relevance_gate_applied",
    "relevance_gate_reason",
    "relevance_gate_threshold",
    "relevance_gate_best_coverage",
    "relevance_gate_filtered_count",
    "project_canonical",
    "project_aliases",
)

_FAILURE_TERMS = (
    "bug",
    "error",
    "fail",
    "failure",
    "failed",
    "fix",
    "regression",
    "wrong",
    "mistake",
    "pitfall",
    "踩坑",
    "失败",
    "错误",
    "报错",
    "修复",
    "质疑",
    "修改",
)

_PREFERENCE_TERMS = (
    "preference",
    "preferences",
    "user preference",
    "user preferences",
    "prefer",
    "prefers",
    "default",
    "defaults",
    "qr",
    "偏好",
    "用户偏好",
    "默认",
)

_QUERY_COVERAGE_STOP_TERMS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "for",
    "from",
    "how",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "use",
    "with",
    "codex",
    "codex++",
    "config",
    "configure",
    "configured",
    "configuration",
    "mcp",
    "memory",
    "rag",
    "template",
    "templates",
    "配置",
    "模板",
    "记忆",
    "检索",
}

_QUERY_COVERAGE_LOW_SIGNAL_CJK_TERMS = {
    "报告",
    "项目",
    "当前",
    "更新",
    "描述",
    "方案",
    "执行",
    "问题",
    "分析",
}

_QUERY_COVERAGE_TOKEN_RE = re.compile(
    r"[A-Za-z][A-Za-z0-9_+\-./]{1,}|\d+(?:\.\d+)+|[\u4e00-\u9fff]{2,}"
)


def _first_line(content: str, limit: int = _TITLE_MAX) -> str:
    """Return the first non-empty line of ``content``, truncated to ``limit``.

    Used to build a stable "title" for compact index entries without loading
    any body text into context.
    """
    if not content:
        return ""
    # Title = first non-empty line; fall back to whole string if none.
    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            content = stripped
            break
    if len(content) > limit:
        return content[:limit] + "..."
    return content


def _copy_recall_diagnostics(source: dict[str, Any], target: dict[str, Any]) -> None:
    for key in _RECALL_DIAGNOSTIC_KEYS:
        if key in source:
            target[key] = source[key]


def _index_entry(item: dict[str, Any]) -> dict[str, Any]:
    """Build a single compact index entry from a standard search item."""
    return {
        "id": item.get("id"),
        "title": _first_line(item.get("content", "") or "", _TITLE_MAX),
        "score": item.get("score", 0.0),
        "type": item.get("type", ""),
        "project": item.get("project", ""),
        "created_at": item.get("created_at", ""),
    }


def index_response(search_result: dict[str, Any]) -> dict[str, Any]:
    """Transform a ``Recall.search`` result into index-only mode.

    Accepts the grouped ``{"results": {type: [items]}}`` shape produced by
    ``Recall.search`` (any detail level) and returns a flat ``results`` list
    of minimal metadata. ``total`` is recomputed to reflect the flattened
    list. ``mode`` is set to ``"index"``. Heavy keys such as ``cognitive``,
    ``expansion`` and ``tiers_used`` are preserved as-is if the caller
    already attached them, but the per-item payload is stripped.
    """
    flat: list[dict[str, Any]] = []
    grouped = search_result.get("results") or {}
    if isinstance(grouped, dict):
        for group in grouped.values():
            if not isinstance(group, list):
                continue
            for item in group:
                if not isinstance(item, dict):
                    continue
                # Items from detail="compact" store the title under "title"
                # rather than "content". Preserve that when available so we
                # don't re-truncate.
                if "content" not in item and "title" in item:
                    entry = {
                        "id": item.get("id"),
                        "title": item.get("title", ""),
                        "score": item.get("score", 0.0),
                        "type": item.get("type", ""),
                        "project": item.get("project", ""),
                        "created_at": item.get("created_at", ""),
                    }
                else:
                    entry = _index_entry(item)
                flat.append(entry)
    # Rank by score desc — gives a stable order independent of type grouping.
    flat.sort(key=lambda e: e.get("score", 0.0), reverse=True)
    out = {
        "query": search_result.get("query"),
        "mode": "index",
        "total": len(flat),
        "results": flat,
    }
    # Carry forward useful top-level metadata when present.
    for key in ("fusion", "tiers_used", "auto_detail"):
        if key in search_result:
            out[key] = search_result[key]
    _copy_recall_diagnostics(search_result, out)
    return out


# --- RAG mode ---------------------------------------------------------------


def _parse_tags(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(t) for t in raw]
    if isinstance(raw, str):
        try:
            loaded = json.loads(raw)
        except Exception:
            return [raw] if raw else []
        if isinstance(loaded, list):
            return [str(t) for t in loaded]
        return [str(loaded)]
    return [str(raw)]


def _flat_hits(search_result: dict[str, Any]) -> list[dict[str, Any]]:
    flat: list[dict[str, Any]] = []
    grouped = search_result.get("results") or {}
    if isinstance(grouped, dict):
        for group in grouped.values():
            if isinstance(group, list):
                flat.extend(i for i in group if isinstance(i, dict))
    return flat


def _normalise_for_dedupe(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "", text)
    return text[:_RAG_DEDUPE_MAX]


def _fallback_summary(content: str) -> str:
    content = re.sub(r"\s+", " ", (content or "").strip())
    if len(content) <= _RAG_SUMMARY_MAX:
        return content
    return content[:_RAG_SUMMARY_MAX] + "..."


def _cached_summaries(store: Any, ids: list[int]) -> dict[int, tuple[str, str]]:
    if store is None or not ids:
        return {}
    try:
        placeholders = ",".join("?" * len(ids))
        rows = store.db.execute(
            "SELECT knowledge_id, representation, content "
            "FROM knowledge_representations "
            f"WHERE knowledge_id IN ({placeholders}) "
            "AND representation IN ('summary', 'compressed')",
            ids,
        ).fetchall()
    except Exception:
        return {}

    ranked = {"summary": 0, "compressed": 1}
    out: dict[int, tuple[str, str]] = {}
    for row in rows:
        kid = int(row["knowledge_id"])
        rep = str(row["representation"])
        content = str(row["content"] or "")
        if not content:
            continue
        existing = out.get(kid)
        if existing is None or ranked.get(rep, 99) < ranked.get(existing[1], 99):
            out[kid] = (content, rep)
    return out


def _query_has_failure_intent(query: str) -> bool:
    q = (query or "").lower()
    return any(term in q for term in _FAILURE_TERMS)


def _query_has_preference_intent(query: str) -> bool:
    q = (query or "").lower()
    return any(term in q for term in _PREFERENCE_TERMS)


def _query_terms(query: str) -> set[str]:
    return {
        t.lower()
        for t in _QUERY_COVERAGE_TOKEN_RE.findall(query or "")
    }


def _query_coverage_terms(query: str) -> list[str]:
    """Return high-signal query terms for precision reranking."""
    out: list[str] = []
    seen: set[str] = set()
    for raw_term in _QUERY_COVERAGE_TOKEN_RE.findall(query or ""):
        term_key = raw_term.lower()
        if term_key in _QUERY_COVERAGE_STOP_TERMS:
            continue
        if re.fullmatch(r"[\u4e00-\u9fff]{2,}", raw_term):
            if raw_term in _QUERY_COVERAGE_LOW_SIGNAL_CJK_TERMS:
                continue
            if raw_term.endswith("项目"):
                continue
            term = raw_term
        elif re.fullmatch(r"\d+(?:\.\d+)+", raw_term):
            term = raw_term
        elif re.fullmatch(r"[A-Z][A-Z0-9]{1,3}", raw_term):
            term = raw_term
        elif re.search(r"[-_+./]", raw_term) or len(raw_term) >= 4:
            term = term_key
        else:
            continue
        if term.lower() in seen:
            continue
        seen.add(term.lower())
        out.append(term)
    return sorted(out, key=lambda value: value.lower())


def _query_coverage(
    item: dict[str, Any],
    *,
    content: str,
    summary: str,
    query_terms: list[str],
) -> tuple[float, list[str]]:
    if not query_terms:
        return 0.0, []
    tags = " ".join(_parse_tags(item.get("tags", [])))
    haystack = " ".join(
        str(part or "")
        for part in (
            content,
            item.get("context", ""),
            tags,
        )
    ).lower()
    matched = [
        term for term in query_terms
        if _query_coverage_term_matches(term, haystack)
    ]
    return len(matched) / len(query_terms), matched


def _query_coverage_term_matches(term: str, haystack: str) -> bool:
    term_key = term.lower()
    if re.search(r"[\u4e00-\u9fff]", term_key):
        return term_key in haystack
    return bool(
        re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(term_key)}(?![A-Za-z0-9_])",
            haystack,
        )
    )


def _rag_score(
    item: dict[str, Any],
    *,
    query: str,
    phase: str | None,
    content: str = "",
    summary: str = "",
    coverage_terms: list[str] | None = None,
) -> tuple[float, bool, bool, bool, float, list[str]]:
    base = float(item.get("rrf_score", item.get("score", 0.0)) or 0.0)
    ktype = str(item.get("type", "") or "").lower()
    tags = [t.lower() for t in _parse_tags(item.get("tags", []))]
    failure = _query_has_failure_intent(query)
    preference = _query_has_preference_intent(query)
    phase_match = bool(phase and f"phase:{phase}".lower() in tags)
    coverage, matched_terms = _query_coverage(
        item,
        content=content,
        summary=summary,
        query_terms=coverage_terms or [],
    )

    if failure:
        if ktype in {"solution", "lesson"}:
            base *= 1.35
        elif any(t in {"errors", "error", "pitfalls", "bugfix"} for t in tags):
            base *= 1.15
    if preference:
        has_preference_layer = "layer:preference" in tags or "layer-preference" in tags
        has_user_preference = "user-preference" in tags
        is_governance = (
            "memory-governance" in tags
            or "preference-layer" in tags
            or "layer-cleanup" in tags
            or "decision" in tags
        )
        if has_preference_layer and has_user_preference and not is_governance:
            base *= 1.45
            generic = {"layer:preference", "layer-preference", "user-preference"}
            specific_tags = {t for t in tags if t not in generic}
            if _query_terms(query) & specific_tags:
                base *= 1.3
        elif has_preference_layer and has_user_preference:
            base *= 1.15
        elif is_governance:
            base *= 0.82
        elif has_user_preference:
            base *= 0.95
        else:
            base *= 0.75
    if phase_match:
        base *= 1.15
    if coverage:
        base *= 1.0 + (0.45 * coverage)
        if coverage >= 0.999:
            base *= 1.25
    return base, failure, phase_match, preference, coverage, matched_terms


def rag_response(
    search_result: dict[str, Any],
    store: Any | None = None,
    *,
    query: str = "",
    phase: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """Return a compact RAG context plan.

    The output is intentionally not full memory content. It is a deduplicated,
    phase-aware shortlist with cached summaries when available and IDs for
    selective follow-up through ``memory_get``.
    """
    hits = _flat_hits(search_result)
    ids = [int(i["id"]) for i in hits if isinstance(i.get("id"), int)]
    summaries = _cached_summaries(store, ids)

    entries_by_key: dict[str, dict[str, Any]] = {}
    effective_query = query or search_result.get("query", "")
    failure_intent = _query_has_failure_intent(effective_query)
    preference_intent = _query_has_preference_intent(effective_query)
    coverage_terms = _query_coverage_terms(effective_query)
    for item in hits:
        kid = item.get("id")
        if not isinstance(kid, int):
            continue
        content = str(item.get("content") or item.get("title") or "")
        cached = summaries.get(kid)
        if cached:
            summary, source = cached
            summary = _fallback_summary(summary)
        else:
            summary, source = _fallback_summary(content), "fallback"
        key = _normalise_for_dedupe(summary or content)
        if not key:
            key = f"id:{kid}"

        score, _failure, phase_match, preference_match, coverage, matched_terms = _rag_score(
            item,
            query=effective_query,
            phase=phase,
            content=content,
            summary=summary,
            coverage_terms=coverage_terms,
        )
        entry = {
            "id": kid,
            "title": _first_line(content, _TITLE_MAX),
            "summary": summary,
            "summary_source": source,
            "type": item.get("type", ""),
            "project": item.get("project", ""),
            "via": item.get("via", []),
            "score": round(score, 6),
            "importance": item.get("importance", "medium"),
            "created_at": item.get("created_at", ""),
            "related_ids": [kid],
            "duplicate_count": 1,
            "phase_match": phase_match,
            "preference_match": preference_match,
            "query_coverage": round(coverage, 3),
            "matched_query_terms": matched_terms,
        }
        if "rrf_score" in item:
            entry["rrf_score"] = item.get("rrf_score")

        existing = entries_by_key.get(key)
        if existing is None:
            entries_by_key[key] = entry
            continue
        existing["related_ids"].append(kid)
        existing["duplicate_count"] += 1
        if score > float(existing.get("score", 0.0)):
            entry["related_ids"] = existing["related_ids"]
            entry["duplicate_count"] = existing["duplicate_count"]
            entries_by_key[key] = entry

    entries = sorted(entries_by_key.values(), key=lambda e: e.get("score", 0.0), reverse=True)
    if limit is not None and limit > 0:
        entries = entries[:limit]

    total_tokens = 0
    for entry in entries:
        est = max(1, len(json.dumps(entry, ensure_ascii=False)) // 4)
        entry["_tokens"] = est
        total_tokens += est

    out = {
        "query": search_result.get("query"),
        "mode": "rag",
        "total": len(entries),
        "candidate_total": len(hits),
        "total_tokens": total_tokens,
        "strategy": {
            "retrieval": "index_then_selective_full",
            "dedupe": "normalized_summary_or_content",
            "summary_cache": "knowledge_representations(summary, compressed) with fallback",
            "failure_priority": failure_intent,
            "preference_priority": preference_intent,
            "phase": phase or "",
            "next_step": "Call memory_get(ids=[...]) only for entries whose summaries are relevant.",
        },
        "results": entries,
    }
    _copy_recall_diagnostics(search_result, out)
    return out


# ── timeline mode ─────────────────────────────────────────────


def _flatten(search_result: dict[str, Any]) -> list[dict[str, Any]]:
    flat: list[dict[str, Any]] = []
    grouped = search_result.get("results") or {}
    if isinstance(grouped, dict):
        for group in grouped.values():
            if isinstance(group, list):
                flat.extend(i for i in group if isinstance(i, dict))
    return flat


def _compact_neighbor(row: Any) -> dict[str, Any]:
    """Render a DB row as a compact timeline neighbour entry."""
    # sqlite3.Row supports dict-like access
    content = row["content"] if "content" in row.keys() else ""
    return {
        "id": row["id"],
        "title": _first_line(content or "", _TITLE_MAX),
        "type": row["type"] if "type" in row.keys() else "",
        "project": row["project"] if "project" in row.keys() else "",
        "created_at": row["created_at"] if "created_at" in row.keys() else "",
        "session_id": row["session_id"] if "session_id" in row.keys() else "",
        "via": ["timeline_neighbor"],
    }


def _fetch_neighbors(
    store: Any,
    *,
    session_id: str,
    created_at: str,
    exclude_ids: set[int],
    neighbors: int,
) -> list[dict[str, Any]]:
    """Return up to ``neighbors`` before and ``neighbors`` after the anchor.

    Preference: records in the same ``session_id``. When there aren't enough
    session peers (or session_id is empty), fall back to global chronology
    by ``created_at``. ``exclude_ids`` is mutated to prevent duplicates
    bubbling up across anchors.
    """
    if neighbors <= 0:
        return []

    collected: list[dict[str, Any]] = []
    db = store.db

    def _rows_to_entries(rows: list[Any]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for r in rows:
            kid = r["id"]
            if kid in exclude_ids:
                continue
            exclude_ids.add(kid)
            out.append(_compact_neighbor(r))
        return out

    # Same-session before/after by created_at
    if session_id:
        before = db.execute(
            "SELECT id, session_id, type, content, project, created_at "
            "FROM knowledge WHERE session_id=? AND status='active' "
            "AND created_at < ? ORDER BY created_at DESC LIMIT ?",
            (session_id, created_at, neighbors),
        ).fetchall()
        after = db.execute(
            "SELECT id, session_id, type, content, project, created_at "
            "FROM knowledge WHERE session_id=? AND status='active' "
            "AND created_at > ? ORDER BY created_at ASC LIMIT ?",
            (session_id, created_at, neighbors),
        ).fetchall()
        collected.extend(_rows_to_entries(list(before)))
        collected.extend(_rows_to_entries(list(after)))

    # Fallback — global chronology when session peers are sparse or absent.
    need_before = neighbors - sum(
        1 for e in collected if e.get("created_at", "") < created_at
    )
    need_after = neighbors - sum(
        1 for e in collected if e.get("created_at", "") > created_at
    )
    if need_before > 0:
        rows = db.execute(
            "SELECT id, session_id, type, content, project, created_at "
            "FROM knowledge WHERE status='active' AND created_at < ? "
            "ORDER BY created_at DESC LIMIT ?",
            (created_at, need_before * 3),
        ).fetchall()
        added = 0
        for r in rows:
            if added >= need_before:
                break
            if r["id"] in exclude_ids:
                continue
            exclude_ids.add(r["id"])
            collected.append(_compact_neighbor(r))
            added += 1
    if need_after > 0:
        rows = db.execute(
            "SELECT id, session_id, type, content, project, created_at "
            "FROM knowledge WHERE status='active' AND created_at > ? "
            "ORDER BY created_at ASC LIMIT ?",
            (created_at, need_after * 3),
        ).fetchall()
        added = 0
        for r in rows:
            if added >= need_after:
                break
            if r["id"] in exclude_ids:
                continue
            exclude_ids.add(r["id"])
            collected.append(_compact_neighbor(r))
            added += 1
    return collected


def timeline_response(
    search_result: dict[str, Any],
    store: Any,
    neighbors: int = 2,
    limit: int = 5,
) -> dict[str, Any]:
    """Expand top-K search hits with ±neighbours and return chronological list.

    Each anchor hit keeps its full payload (as returned by the underlying
    search) and is marked with ``role='hit'``. Neighbours get ``role=
    'neighbor'`` with compact fields. The final list is sorted by
    ``created_at`` ascending so the caller reads it like a session diary.
    """
    flat = _flatten(search_result)
    # Respect limit: only expand top-K hits.
    hits = flat[: max(0, int(limit))]

    seen: set[int] = {int(h["id"]) for h in hits if isinstance(h.get("id"), int)}
    timeline_items: list[dict[str, Any]] = []

    for hit in hits:
        anchor = dict(hit)
        anchor["role"] = "hit"
        timeline_items.append(anchor)

        session_id = hit.get("session_id", "") or ""
        created_at = hit.get("created_at", "") or ""
        if not created_at:
            continue
        nbrs = _fetch_neighbors(
            store,
            session_id=session_id,
            created_at=created_at,
            exclude_ids=seen,
            neighbors=neighbors,
        )
        for n in nbrs:
            n["role"] = "neighbor"
            timeline_items.append(n)

    timeline_items.sort(key=lambda e: e.get("created_at", "") or "")

    out = {
        "query": search_result.get("query"),
        "mode": "timeline",
        "total": len(timeline_items),
        "hits": len(hits),
        "neighbors": neighbors,
        "results": timeline_items,
    }
    for key in ("fusion", "tiers_used"):
        if key in search_result:
            out[key] = search_result[key]
    _copy_recall_diagnostics(search_result, out)
    return out
