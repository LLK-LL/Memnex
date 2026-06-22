"""
Built-in evaluation harness — v7.0 Phase F.

Runs structured test scenarios against the memory system and produces a
report with:
  - recall_at_k (R@1, R@5, R@10)
  - prevention_rate (% of known bug patterns caught by file_context)
  - latency_p50_ms, latency_p95_ms, mean_latency_ms
  - per-scenario pass/fail

Scenarios are loaded from `evals/scenarios/*.json`. Each scenario is one of:
  - {"type": "recall", "query": "...", "project": "...", "must_contain": ["..."]}
  - {"type": "prevention", "file": "...", "project": "...",
     "must_warn_about": ["pattern-key"]}
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

DEFAULT_SCENARIOS_DIR = Path(__file__).parent.parent / "evals" / "scenarios"


@dataclass
class ScenarioResult:
    name: str
    type: str
    passed: bool
    latency_ms: float
    details: dict[str, Any] = field(default_factory=dict)


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    k = (len(s) - 1) * p
    f, c = int(k), min(int(k) + 1, len(s) - 1)
    if f == c:
        return s[f]
    return s[f] + (s[c] - s[f]) * (k - f)


class EvalHarness:
    """Evaluation harness driving recall + prevention scenarios."""

    def __init__(
        self,
        *,
        recall_fn: Callable[[str, dict[str, Any]], list[dict[str, Any]]] | None = None,
        file_warnings_fn: Callable[[str, dict[str, Any]], dict[str, Any]] | None = None,
    ) -> None:
        self.recall_fn = recall_fn
        self.file_warnings_fn = file_warnings_fn

    # ──────────────────────────────────────────────
    # Scenario loading
    # ──────────────────────────────────────────────

    def load_scenarios(
        self,
        source: str | Path | list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        if source is None:
            source = DEFAULT_SCENARIOS_DIR
        if isinstance(source, list):
            return list(source)
        path = Path(source)
        scenarios: list[dict[str, Any]] = []
        if path.is_dir():
            for f in sorted(path.glob("*.json")):
                with open(f, encoding="utf-8") as fh:
                    data = json.load(fh)
                    if isinstance(data, list):
                        scenarios.extend(data)
                    elif isinstance(data, dict):
                        scenarios.append(data)
        elif path.is_file():
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
                scenarios = data if isinstance(data, list) else [data]
        return scenarios

    # ──────────────────────────────────────────────
    # Run a single scenario
    # ──────────────────────────────────────────────

    def run_scenario(self, scenario: dict[str, Any]) -> ScenarioResult:
        stype = scenario.get("type", "recall")
        name = scenario.get("name", f"<{stype}>")
        start = time.perf_counter()
        passed = False
        details: dict[str, Any] = {}

        try:
            if stype == "recall":
                passed, details = self._run_recall(scenario)
            elif stype == "prevention":
                passed, details = self._run_prevention(scenario)
            else:
                details = {"error": f"unknown scenario type: {stype}"}
        except Exception as e:  # pragma: no cover — harness should never crash
            details = {"error": f"{type(e).__name__}: {e}"}

        latency_ms = (time.perf_counter() - start) * 1000.0
        return ScenarioResult(
            name=name, type=stype, passed=passed,
            latency_ms=latency_ms, details=details,
        )

    def _run_recall(self, scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        if self.recall_fn is None:
            return False, {"error": "recall_fn not configured"}
        query = scenario["query"]
        must_contain = scenario.get("must_contain", [])
        expected_terms = scenario.get("expected_terms", [])
        expected_ids = [int(i) for i in scenario.get("expected_ids", [])]
        required_terms = list(dict.fromkeys([*must_contain, *expected_terms]))
        k = scenario.get("k", 5)
        params = {
            "project": scenario.get("project"),
            "limit": max(k, len(required_terms) or len(expected_ids) or 1),
        }
        hits = self.recall_fn(query, params) or []
        top_hits = hits[:k]
        hit_texts = [str(h.get("content", "")) for h in top_hits]
        hit_ids = [
            int(h["id"]) for h in top_hits
            if isinstance(h.get("id"), int) or str(h.get("id", "")).isdigit()
        ]
        blob = " ".join(hit_texts).lower()
        missing_terms = [m for m in required_terms if m.lower() not in blob]
        missing_ids = [i for i in expected_ids if i not in hit_ids]

        id_rank = None
        if expected_ids:
            expected_set = set(expected_ids)
            for idx, hit in enumerate(hits, start=1):
                hid = hit.get("id")
                if (isinstance(hid, int) or str(hid).isdigit()) and int(hid) in expected_set:
                    id_rank = idx
                    break

        term_rank = None
        for idx, text in enumerate(hit_texts, start=1):
            if required_terms and any(m.lower() in text.lower() for m in required_terms):
                term_rank = idx
                break

        rank = id_rank if id_rank is not None else term_rank
        passed = len(missing_terms) == 0 and len(missing_ids) == 0
        return passed, {
            "query": query,
            "k": k,
            "hits": len(hits),
            "hit_ids": hit_ids,
            "expected_ids": expected_ids,
            "missing_ids": missing_ids,
            "missing": missing_terms,
            "missing_terms": missing_terms,
            "first_match_rank": rank,
            "reciprocal_rank": round(1.0 / rank, 4) if rank else 0.0,
        }

    def _run_prevention(self, scenario: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
        if self.file_warnings_fn is None:
            return False, {"error": "file_warnings_fn not configured"}
        file = scenario["file"]
        must_warn = scenario.get("must_warn_about", [])
        params = {"project": scenario.get("project")}
        result = self.file_warnings_fn(file, params) or {}

        warnings = result.get("warnings", [])
        rules = result.get("related_rules", [])
        blob_parts: list[str] = []
        for w in warnings:
            for k in ("content", "context", "fix"):
                if w.get(k):
                    blob_parts.append(str(w[k]))
        for r in rules:
            for k in ("content", "context"):
                if r.get(k):
                    blob_parts.append(str(r[k]))
        blob = " ".join(blob_parts).lower()
        missing = [p for p in must_warn if p.lower() not in blob]
        passed = len(missing) == 0 and (len(warnings) > 0 or len(rules) > 0)
        return passed, {
            "file": file,
            "warnings_count": len(warnings),
            "rules_count": len(rules),
            "missing": missing,
            "risk_score": result.get("risk_score"),
        }

    # ──────────────────────────────────────────────
    # Full suite
    # ──────────────────────────────────────────────

    def run_suite(
        self,
        source: str | Path | list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        scenarios = self.load_scenarios(source)
        results = [self.run_scenario(s) for s in scenarios]

        recall_results = [r for r in results if r.type == "recall"]
        prevention_results = [r for r in results if r.type == "prevention"]

        recall_passed = sum(1 for r in recall_results if r.passed)
        prevention_passed = sum(1 for r in prevention_results if r.passed)

        # Recall@k variants — based on first_match_rank
        ranks = [r.details.get("first_match_rank")
                 for r in recall_results
                 if r.details.get("first_match_rank")]
        reciprocal_ranks = [
            float(r.details.get("reciprocal_rank", 0.0))
            for r in recall_results
        ]
        def _rak(k: int) -> float:
            if not recall_results:
                return 0.0
            hits = sum(1 for r in ranks if r <= k)
            return hits / len(recall_results)

        latencies = [r.latency_ms for r in results]

        return {
            "total": len(results),
            "passed": recall_passed + prevention_passed,
            "failed": len(results) - (recall_passed + prevention_passed),
            "recall": {
                "total": len(recall_results),
                "passed": recall_passed,
                "r_at_1": round(_rak(1), 4),
                "r_at_5": round(_rak(5), 4),
                "r_at_10": round(_rak(10), 4),
                "mrr": round(
                    sum(reciprocal_ranks) / len(reciprocal_ranks), 4,
                ) if reciprocal_ranks else 0.0,
            },
            "prevention": {
                "total": len(prevention_results),
                "passed": prevention_passed,
                "rate": round(prevention_passed / len(prevention_results), 4)
                        if prevention_results else 0.0,
            },
            "latency": {
                "mean_ms": round(sum(latencies) / len(latencies), 3) if latencies else 0.0,
                "p50_ms": round(_percentile(latencies, 0.50), 3),
                "p95_ms": round(_percentile(latencies, 0.95), 3),
                "max_ms": round(max(latencies), 3) if latencies else 0.0,
            },
            "scenarios": [
                {
                    "name": r.name, "type": r.type,
                    "passed": r.passed, "latency_ms": round(r.latency_ms, 3),
                    "details": r.details,
                }
                for r in results
            ],
        }


def write_jsonl_report(report: dict[str, Any], output_path: str | Path) -> str:
    """Append one eval report snapshot for trend monitoring."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        **report,
    }
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return str(path)
