#!/usr/bin/env python3
"""Report passive recall-monitor JSONL metrics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_src_dir = str(Path(__file__).resolve().parent.parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from recall_monitor import render_markdown, summarize_log


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Summarize RAG/rule recall monitor events.")
    parser.add_argument("--log", default=None, help="Path to recall-monitor JSONL log.")
    parser.add_argument("--days", type=int, default=7, help="Window size in days.")
    parser.add_argument(
        "--layer",
        choices=["all", "memory", "rule"],
        default="all",
        help="Only summarize one recall layer.",
    )
    parser.add_argument("--recent", type=int, default=5, help="Recent recall-content samples to show.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    args = parser.parse_args(argv)

    summary = summarize_log(args.log, days=args.days, layer=args.layer, recent_limit=args.recent)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_markdown(summary), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
