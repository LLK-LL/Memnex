from __future__ import annotations

import json
from datetime import datetime, timezone

from src.recall_monitor import (
    build_event,
    record_recall_event,
    render_markdown,
    summarize_events,
    summarize_log,
)


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

    record_recall_event(
        "memory_recall",
        {"query": "memory RAG monitor", "project": "tam"},
        {
            "mode": "rag",
            "results": [{"id": 10, "summary": "Memory RAG monitor hit", "score": 0.1}],
        },
        log_path=log,
        now=datetime(2026, 7, 6, tzinfo=timezone.utc),
    )
    record_recall_event(
        "rule_context_refresh",
        {"latest_user_instruction": "rule monitor", "project": "tam"},
        {
            "rules": [{"id": 20, "content": "Rule monitor hit", "category": "test"}],
            "counts": {"always_on": 0, "contextual": 1, "total": 1},
        },
        log_path=log,
        now=datetime(2026, 7, 6, tzinfo=timezone.utc),
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
