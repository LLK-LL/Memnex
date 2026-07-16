from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.recall_monitor import (
    build_event,
    record_recall_event,
    render_markdown,
    summarize_events,
    summarize_log,
)


def _load_recall_quality_repair_cases():
    fixture = Path(__file__).parent / "fixtures" / "recall_quality_repair_cases.json"
    return json.loads(fixture.read_text(encoding="utf-8"))


def test_memory_recall_event_marks_proxy_hit_from_overlap(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMORY_RECALL_MONITOR", "1")
    log = tmp_path / "recall-monitor.jsonl"

    event = record_recall_event(
        "memory_recall",
        {"query": "memory RAG monitor", "project": "tam", "mode": "rag"},
        {
            "mode": "rag",
            "total": 1,
            "candidate_total": 3,
            "results": [
                {
                    "id": 7,
                    "type": "solution",
                    "title": "Memory RAG monitor design",
                    "summary": "Track memory RAG monitor calls.",
                    "score": 0.07,
                }
            ],
        },
        log_path=log,
        now=datetime(2026, 7, 5, tzinfo=timezone.utc),
    )

    assert event is not None
    assert event["proxy"]["verdict"] == "likely_hit"
    saved = json.loads(log.read_text(encoding="utf-8").strip())
    assert saved["event_type"] == "memory_recall"
    assert saved["query_hash"]
    assert saved["top_results"][0]["id"] == 7


def test_memory_recall_event_records_routing_gate_and_result_metadata():
    event = build_event(
        "memory_recall",
        {"query": "energy curve", "project": "demo", "mode": "rag"},
        {
            "mode": "rag",
            "total": 1,
            "candidate_total": 1,
            "graph_expand_applied": True,
            "graph_expand_reason": "auto_causal",
            "graph_expand_families": ["causal"],
            "routed_via": "hybrid",
            "routed_graph_families": ["causal", "procedural"],
            "relevance_gate_applied": True,
            "relevance_gate_reason": "passed",
            "relevance_gate_threshold": 0.1,
            "relevance_gate_best_coverage": 1.0,
            "relevance_gate_filtered_count": 2,
            "results": [{
                "id": 8,
                "type": "fact",
                "title": "Energy curve processing",
                "summary": "Energy curve processing details.",
                "project": "demo",
                "via": ["fts", "graph_expand"],
                "score": 0.08,
                "query_coverage": 1.0,
                "matched_query_terms": ["energy", "curve"],
            }],
        },
        now=datetime(2026, 7, 10, tzinfo=timezone.utc),
    )

    assert event["graph_expand_applied"] is True
    assert event["graph_expand_reason"] == "auto_causal"
    assert event["graph_expand_families"] == ["causal"]
    assert event["routed_via"] == "hybrid"
    assert event["routed_graph_families"] == ["causal", "procedural"]
    assert event["relevance_gate_reason"] == "passed"
    assert event["relevance_gate_filtered_count"] == 2
    assert event["top_results"][0]["project"] == "demo"
    assert event["top_results"][0]["via"] == ["fts", "graph_expand"]
    assert event["top_results"][0]["query_coverage"] == 1.0
    assert event["top_results"][0]["matched_query_terms"] == ["energy", "curve"]


def test_lower_rank_overlap_alone_remains_unknown():
    event = build_event(
        "memory_recall",
        {"query": "alpha beta", "project": "demo", "mode": "rag"},
        {
            "mode": "rag",
            "total": 2,
            "results": [
                {"id": 1, "title": "unrelated first result", "score": 0.1},
                {"id": 2, "title": "alpha beta exact lower result", "score": 0.09},
            ],
        },
        now=datetime(2026, 7, 10, tzinfo=timezone.utc),
    )

    assert event["proxy"]["verdict"] == "unknown"
    assert event["proxy"]["reason"] == "lower_rank_signal_only"
    assert event["proxy"]["overlap_terms"] == 0


def test_project_report_only_filtered_response_is_not_likely_hit():
    event = build_event(
        "memory_recall",
        {
            "query": "南京理工项目 吸收能量曲线 报告 SPH ALE",
            "project": "南京理工项目",
            "mode": "rag",
        },
        {
            "mode": "rag",
            "total": 0,
            "candidate_total": 1,
            "relevance_gate_applied": True,
            "relevance_gate_reason": "below_minimum",
            "relevance_gate_threshold": 0.25,
            "relevance_gate_best_coverage": 0.0,
            "relevance_gate_filtered_count": 1,
            "results": [],
        },
        now=datetime(2026, 7, 10, tzinfo=timezone.utc),
    )

    assert event["proxy"]["verdict"] != "likely_hit"
    assert event["proxy"]["reason"] == "no_results"
    assert event["relevance_gate_reason"] == "below_minimum"


def test_memory_recall_event_records_effective_phase():
    event = build_event(
        "memory_recall",
        {"query": "build checklist", "project": "demo", "mode": "rag", "phase": "build"},
        {
            "mode": "rag",
            "phase": "build",
            "total": 1,
            "results": [{
                "id": 9,
                "type": "fact",
                "title": "Build checklist",
                "summary": "Build checklist",
                "project": "demo",
                "score": 0.08,
                "phase_match": True,
                "query_coverage": 1.0,
            }],
        },
        now=datetime(2026, 7, 10, tzinfo=timezone.utc),
    )

    assert event["phase"] == "build"
    assert event["top_results"][0]["phase_match"] is True


def test_recall_quality_repair_cases_replay(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMORY_RECALL_MONITOR", "1")
    log = tmp_path / "recall-quality-repair.jsonl"

    for case in _load_recall_quality_repair_cases():
        event = record_recall_event(
            case["event_type"],
            case["request"],
            case["response"],
            log_path=log,
            now=datetime(2026, 7, 10, tzinfo=timezone.utc),
        )
        assert event is not None
        expect = case["expect"]
        if "phase" in expect:
            assert event["phase"] == expect["phase"]
        if "proxy_verdict" in expect:
            assert event["proxy"]["verdict"] == expect["proxy_verdict"]
        if "graph_expand_reason" in expect:
            assert event["graph_expand_reason"] == expect["graph_expand_reason"]

    lines = log.read_text(encoding="utf-8").splitlines()
    assert len(lines) == len(_load_recall_quality_repair_cases())


def test_rule_event_marks_always_on_only_as_unknown():
    event = build_event(
        "rule_context_refresh",
        {"latest_user_instruction": "build a monitor", "project": "tam", "phase": "build"},
        {
            "rules": [{"id": 1, "content": "Always redact secrets.", "category": "security"}],
            "counts": {"always_on": 1, "contextual": 0, "total": 1},
        },
        now=datetime(2026, 7, 5, tzinfo=timezone.utc),
    )

    assert event["proxy"]["verdict"] == "unknown"
    assert event["proxy"]["reason"] == "always_on_only"


def test_summarize_events_excludes_unknown_from_proxy_hit_rate():
    events = [
        {"event_type": "memory_recall", "ts": "2026-07-05T00:00:00Z", "proxy": {"verdict": "likely_hit"}},
        {"event_type": "memory_recall", "ts": "2026-07-05T00:00:01Z", "proxy": {"verdict": "likely_miss"}},
        {"event_type": "rule_context_refresh", "ts": "2026-07-05T00:00:02Z", "proxy": {"verdict": "unknown"}},
    ]

    summary = summarize_events(events)

    assert summary["events"] == 3
    assert summary["proxy_hit_rate"] == 0.5
    assert summary["by_type"]["memory_recall"]["events"] == 2
    rendered = render_markdown({**summary, "window_days": 7, "log_path": "x"})
    assert "Proxy hit rate: 50.0%" in rendered


def test_monitor_can_be_disabled(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMORY_RECALL_MONITOR", "0")
    log = tmp_path / "disabled.jsonl"

    event = record_recall_event("memory_recall", {"query": "x"}, {"results": []}, log_path=log)

    assert event is None
    assert not log.exists()


def test_summary_splits_memory_and_rule_layers_with_recent_content(tmp_path, monkeypatch):
    monkeypatch.setenv("MEMORY_RECALL_MONITOR", "1")
    log = tmp_path / "recall-monitor.jsonl"
    recent_now = datetime.now(timezone.utc) - timedelta(hours=1)

    record_recall_event(
        "memory_recall",
        {"query": "memory RAG monitor", "project": "tam"},
        {
            "mode": "rag",
            "results": [{"id": 10, "summary": "Memory RAG monitor hit", "score": 0.1}],
        },
        log_path=log,
        now=recent_now,
    )
    record_recall_event(
        "rule_context_refresh",
        {"latest_user_instruction": "rule monitor", "project": "tam"},
        {
            "rules": [{"id": 20, "content": "Rule monitor hit", "category": "test"}],
            "counts": {"always_on": 0, "contextual": 1, "total": 1},
        },
        log_path=log,
        now=recent_now,
    )

    all_summary = summarize_log(log, days=7, recent_limit=2)
    memory_summary = summarize_log(log, days=7, layer="memory", recent_limit=2)
    rule_summary = summarize_log(log, days=7, layer="rule", recent_limit=2)

    assert all_summary["by_layer"]["memory_layer"]["events"] == 1
    assert all_summary["by_layer"]["rule_layer"]["events"] == 1
    assert memory_summary["events"] == 1
    assert list(memory_summary["by_layer"]) == ["memory_layer"]
    assert rule_summary["events"] == 1
    assert list(rule_summary["by_layer"]) == ["rule_layer"]
    rendered = render_markdown(all_summary)
    assert "## Recent Recall Content" in rendered
    assert "Memory RAG monitor hit" in rendered
    assert "Rule monitor hit" in rendered
