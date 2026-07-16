"""Passive monitoring for memory and rule recall quality.

The monitor writes local JSONL audit events from the MCP hot path. It uses
deterministic proxy labels only; these are not ground truth relevance labels.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    from paths import memory_dir
except Exception:  # pragma: no cover - import fallback for direct script use
    try:
        from .paths import memory_dir  # type: ignore[no-redef]
    except Exception:
        memory_dir = None  # type: ignore[assignment]


DEFAULT_LOG_NAME = "recall-monitor.jsonl"
MAX_TEXT = 240
MAX_ITEMS = 5

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "how", "i", "in", "is", "it", "of", "on", "or", "that", "the",
    "this", "to", "use", "what", "when", "with", "you", "your",
    "一个", "以及", "使用", "内容", "当前", "我们", "我的", "是否",
}

_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd|pwd)\s*[:=]\s*\S+"),
    re.compile(r"(?i)bearer\s+[a-z0-9._~+/=-]{12,}"),
    re.compile(r"sk-[a-zA-Z0-9_-]{12,}"),
)


def monitor_enabled() -> bool:
    raw = os.environ.get("MEMORY_RECALL_MONITOR", "1").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def default_log_path() -> Path:
    override = os.environ.get("MEMORY_RECALL_MONITOR_LOG")
    if override:
        return Path(override).expanduser()
    root = memory_dir() if memory_dir is not None else Path.home() / ".tam"
    return root / "logs" / DEFAULT_LOG_NAME


def record_recall_event(
    event_type: str,
    request: dict[str, Any],
    response: dict[str, Any],
    *,
    log_path: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, Any] | None:
    """Append one recall-monitor event.

    Returns the event for tests/diagnostics. Runtime callers may ignore it.
    """
    if not monitor_enabled():
        return None
    event = build_event(event_type, request, response, now=now)
    path = Path(log_path) if log_path is not None else default_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    return event


def build_event(
    event_type: str,
    request: dict[str, Any],
    response: dict[str, Any],
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    ts = now or datetime.now(timezone.utc)
    query = _event_query(request, response)
    query_text = _safe_text(query)
    event: dict[str, Any] = {
        "schema": "recall-monitor.v1",
        "ts": ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "event_type": event_type,
        "tool": request.get("_tool") or event_type,
        "layer": _event_layer(event_type),
        "project": request.get("project") or response.get("project") or "general",
        "phase": request.get("phase") or response.get("phase") or response.get("phase_filter") or "",
        "query_hash": _hash_text(query),
        "query": query_text,
    }
    if event_type == "memory_recall":
        event.update(_memory_payload(request, response, query))
    elif event_type in {"self_rules_context", "rule_context_refresh"}:
        event.update(_rule_payload(response, query))
    else:
        event["proxy"] = _proxy("unknown", "unsupported_event_type")
    return event


def summarize_events(
    events: Iterable[dict[str, Any]],
    *,
    since: datetime | None = None,
    layer: str = "all",
    recent_limit: int = 5,
) -> dict[str, Any]:
    totals: dict[str, Any] = {
        "events": 0,
        "by_type": {},
        "by_layer": {},
        "verdicts": {},
        "proxy_hit_rate": None,
        "retrieval_tiers": {},
        "graph_result_rate": None,
        "recent": [],
    }
    by_type: dict[str, Counter] = defaultdict(Counter)
    by_layer: dict[str, Counter] = defaultdict(Counter)
    verdicts: Counter = Counter()
    hit_miss_total = 0
    hit_total = 0
    recent: list[dict[str, Any]] = []
    retrieval_tiers: Counter = Counter()
    memory_events = 0
    graph_events = 0

    for event in events:
        if since is not None:
            try:
                event_ts = datetime.fromisoformat(str(event["ts"]).replace("Z", "+00:00"))
            except Exception:
                continue
            if event_ts < since:
                continue
        event_layer = str(event.get("layer") or _event_layer(str(event.get("event_type") or "")))
        if layer != "all" and event_layer != f"{layer}_layer":
            continue
        etype = str(event.get("event_type") or "unknown")
        verdict = str((event.get("proxy") or {}).get("verdict") or "unknown")
        totals["events"] += 1
        by_type[etype]["events"] += 1
        by_type[etype][verdict] += 1
        by_layer[event_layer]["events"] += 1
        by_layer[event_layer][verdict] += 1
        verdicts[verdict] += 1
        if event_layer == "memory_layer":
            memory_events += 1
            event_has_graph = False
            for item in event.get("top_results") or []:
                via = item.get("via") or []
                if isinstance(via, str):
                    via = [via]
                for tier in via:
                    tier_name = str(tier)
                    retrieval_tiers[tier_name] += 1
                    if tier_name in {"graph", "graph_expand"}:
                        event_has_graph = True
            if event_has_graph:
                graph_events += 1
        if verdict in {"likely_hit", "likely_miss"}:
            hit_miss_total += 1
            if verdict == "likely_hit":
                hit_total += 1
        if recent_limit > 0:
            recent.append(_compact_recent_event(event, event_layer))
            if len(recent) > recent_limit:
                recent.pop(0)

    totals["by_type"] = {k: dict(v) for k, v in sorted(by_type.items())}
    totals["by_layer"] = {k: dict(v) for k, v in sorted(by_layer.items())}
    totals["verdicts"] = dict(verdicts)
    totals["retrieval_tiers"] = dict(retrieval_tiers)
    if memory_events:
        totals["graph_result_rate"] = round(graph_events / memory_events, 4)
    totals["recent"] = recent
    if hit_miss_total:
        totals["proxy_hit_rate"] = round(hit_total / hit_miss_total, 4)
    return totals


def load_events(path: str | Path | None = None) -> list[dict[str, Any]]:
    log_path = Path(path) if path is not None else default_log_path()
    if not log_path.exists():
        return []
    events: list[dict[str, Any]] = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return events


def summarize_log(
    path: str | Path | None = None,
    *,
    days: int = 7,
    layer: str = "all",
    recent_limit: int = 5,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=max(1, int(days)))
    events = load_events(path)
    summary = summarize_events(events, since=since, layer=layer, recent_limit=recent_limit)
    summary["window_days"] = max(1, int(days))
    summary["layer_filter"] = layer
    summary["log_path"] = str(Path(path) if path is not None else default_log_path())
    return summary


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Recall Monitor Report",
        "",
        f"- Window: {summary.get('window_days', '?')} days",
        f"- Layer: {summary.get('layer_filter', 'all')}",
        f"- Events: {summary.get('events', 0)}",
        f"- Proxy hit rate: {_format_rate(summary.get('proxy_hit_rate'))}",
        f"- Graph result rate: {_format_rate(summary.get('graph_result_rate'))}",
        f"- Log: `{summary.get('log_path', '')}`",
        "",
        "## By Layer",
    ]
    by_layer = summary.get("by_layer") or {}
    if by_layer:
        for layer_name, counts in by_layer.items():
            lines.append(
                f"- {layer_name}: {counts.get('events', 0)} events, "
                f"likely_hit={counts.get('likely_hit', 0)}, "
                f"likely_miss={counts.get('likely_miss', 0)}, "
                f"unknown={counts.get('unknown', 0)}"
            )
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## By Event Type",
    ])
    by_type = summary.get("by_type") or {}
    if not by_type:
        lines.append("")
        lines.append("No monitor events in this window.")
        return "\n".join(lines) + "\n"
    for event_type, counts in by_type.items():
        lines.append(
            f"- {event_type}: {counts.get('events', 0)} events, "
            f"likely_hit={counts.get('likely_hit', 0)}, "
            f"likely_miss={counts.get('likely_miss', 0)}, "
            f"unknown={counts.get('unknown', 0)}"
        )
    recent = summary.get("recent") or []
    if recent:
        lines.append("")
        lines.append("## Recent Recall Content")
        for event in recent:
            lines.append(
                f"- {event.get('ts', '')} {event.get('layer', '')} "
                f"{event.get('verdict', '')}: {event.get('query', '')}"
            )
            for item in event.get("items", []):
                label = item.get("title") or item.get("content") or ""
                prefix = f"  - #{item.get('id')}" if item.get("id") is not None else "  -"
                lines.append(f"{prefix} {label}")
    return "\n".join(lines) + "\n"


def _memory_payload(request: dict[str, Any], response: dict[str, Any], query: str) -> dict[str, Any]:
    results = response.get("results") or []
    if isinstance(results, dict):
        flat = []
        for group in results.values():
            if isinstance(group, list):
                flat.extend(i for i in group if isinstance(i, dict))
        results = flat
    if not isinstance(results, list):
        results = []
    results = sorted(
        (item for item in results if isinstance(item, dict)),
        key=lambda item: _float(item.get("rrf_score", item.get("score", 0.0))),
        reverse=True,
    )

    top_results = []
    top_overlap = 0
    top_score = 0.0
    top_signal = False
    lower_rank_signal = False
    for index, item in enumerate(results[:MAX_ITEMS]):
        text = " ".join(str(item.get(k) or "") for k in ("title", "summary", "content"))
        overlap = len(_terms(query) & _terms(text))
        score = _float(item.get("rrf_score", item.get("score", 0.0)))
        query_coverage = _float(item.get("query_coverage", 0.0))
        phase_or_preference = bool(
            item.get("phase_match") or item.get("preference_match")
        )
        item_signal = overlap >= 2 or phase_or_preference or query_coverage >= 0.25
        if index == 0:
            top_overlap = overlap
            top_score = score
            top_signal = item_signal
        elif item_signal:
            lower_rank_signal = True
        via = item.get("via") or []
        if isinstance(via, str):
            via = [via]
        matched_query_terms = item.get("matched_query_terms") or []
        if not isinstance(matched_query_terms, list):
            matched_query_terms = [matched_query_terms]
        top_results.append({
            "id": item.get("id"),
            "type": item.get("type", ""),
            "project": item.get("project", ""),
            "via": [str(value) for value in via],
            "score": score,
            "overlap_terms": overlap,
            "query_coverage": query_coverage,
            "matched_query_terms": [
                _safe_text(value) for value in matched_query_terms[:12]
            ],
            "summary_source": item.get("summary_source", ""),
            "phase_match": bool(item.get("phase_match")),
            "preference_match": bool(item.get("preference_match")),
            "title": _safe_text(item.get("title") or item.get("summary") or item.get("content") or ""),
        })

    total = int(response.get("total") or len(results))
    if total <= 0:
        proxy = _proxy("likely_miss", "no_results", top_overlap, top_score)
    elif top_signal:
        proxy = _proxy("likely_hit", "top_result_signal", top_overlap, top_score)
    elif top_score >= 0.30:
        proxy = _proxy("likely_hit", "high_score", top_overlap, top_score)
    elif lower_rank_signal:
        proxy = _proxy("unknown", "lower_rank_signal_only", top_overlap, top_score)
    else:
        proxy = _proxy(
            "unknown", "returned_without_deterministic_signal", top_overlap, top_score
        )

    payload = {
        "mode": response.get("mode") or request.get("mode", "rag"),
        "limit": request.get("limit"),
        "total": total,
        "candidate_total": response.get("candidate_total"),
        "top_results": top_results,
        "proxy": proxy,
    }
    for key in (
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
    ):
        if key in response:
            payload[key] = response[key]
    return payload


def _rule_payload(response: dict[str, Any], query: str) -> dict[str, Any]:
    rules = response.get("rules") or []
    if not isinstance(rules, list):
        rules = []
    counts = response.get("counts") or {}
    query_filter = response.get("query_filter") or {}
    if not counts and query_filter:
        counts = {
            "always_on": query_filter.get("always_on_count", 0),
            "contextual": query_filter.get("contextual_count", 0),
            "total": response.get("rules_count", len(rules)),
        }

    top_rules = []
    best_overlap = 0
    for rule in rules[:MAX_ITEMS]:
        if not isinstance(rule, dict):
            continue
        text = str(rule.get("content") or "")
        overlap = len(_terms(query) & _terms(text))
        best_overlap = max(best_overlap, overlap)
        top_rules.append({
            "id": rule.get("id"),
            "category": rule.get("category", ""),
            "priority": rule.get("priority", 0),
            "overlap_terms": overlap,
            "content": _safe_text(text),
        })

    total = int(response.get("rules_count") or counts.get("total") or len(rules))
    contextual = int(counts.get("contextual") or query_filter.get("contextual_count") or 0)
    trigger_matches = query_filter.get("trigger_matches") or []
    if total <= 0:
        proxy = _proxy("likely_miss", "no_rules", best_overlap)
    elif contextual <= 0:
        proxy = _proxy("unknown", "always_on_only", best_overlap)
    elif trigger_matches or best_overlap >= 1:
        proxy = _proxy("likely_hit", "contextual_rule_signal", best_overlap)
    else:
        proxy = _proxy("unknown", "contextual_without_deterministic_signal", best_overlap)

    return {
        "rules_count": total,
        "counts": counts,
        "refresh_reason": response.get("refresh_reason"),
        "cooldown_hit": response.get("cooldown_hit"),
        "top_rules": top_rules,
        "proxy": proxy,
    }


def _event_query(request: dict[str, Any], response: dict[str, Any]) -> str:
    return str(
        request.get("query")
        or request.get("latest_user_instruction")
        or response.get("query")
        or ""
    )


def _event_layer(event_type: str) -> str:
    if event_type == "memory_recall":
        return "memory_layer"
    if event_type in {"self_rules_context", "rule_context_refresh"}:
        return "rule_layer"
    return "unknown_layer"


def _compact_recent_event(event: dict[str, Any], layer: str) -> dict[str, Any]:
    items_key = "top_results" if layer == "memory_layer" else "top_rules"
    items = []
    for item in event.get(items_key, [])[:3]:
        if not isinstance(item, dict):
            continue
        items.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "content": item.get("content"),
            "category": item.get("category"),
            "score": item.get("score"),
        })
    return {
        "ts": event.get("ts", ""),
        "layer": layer,
        "event_type": event.get("event_type", ""),
        "project": event.get("project", ""),
        "phase": event.get("phase", ""),
        "verdict": (event.get("proxy") or {}).get("verdict", ""),
        "reason": (event.get("proxy") or {}).get("reason", ""),
        "query": _safe_text(event.get("query", "")),
        "items": items,
    }


def _safe_text(value: Any) -> str:
    text = " ".join(str(value or "").split())
    for pattern in _SECRET_PATTERNS:
        text = pattern.sub(lambda m: m.group(1) + "=[REDACTED]" if m.groups() else "[REDACTED]", text)
    if len(text) > MAX_TEXT:
        return text[:MAX_TEXT].rstrip() + "..."
    return text


def _hash_text(text: Any) -> str:
    return hashlib.sha256(str(text or "").encode("utf-8")).hexdigest()[:16]


def _terms(text: Any) -> set[str]:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9_+\-./]{1,}|[\u4e00-\u9fff]{2,}", str(text or "").lower())
    return {t for t in tokens if t not in _STOPWORDS and len(t) > 1}


def _float(value: Any) -> float:
    try:
        return round(float(value), 6)
    except (TypeError, ValueError):
        return 0.0


def _proxy(verdict: str, reason: str, overlap_terms: int = 0, score: float = 0.0) -> dict[str, Any]:
    return {
        "verdict": verdict,
        "reason": reason,
        "overlap_terms": int(overlap_terms),
        "score": _float(score),
    }


def _format_rate(value: Any) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return "n/a"
