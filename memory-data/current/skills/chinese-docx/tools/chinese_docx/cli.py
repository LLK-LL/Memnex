from __future__ import annotations

import argparse
import json
from pathlib import Path

from chinese_docx.inspect import inspect_docx
from chinese_docx.repair import repair_docx


def main() -> None:
    parser = argparse.ArgumentParser(prog="chinese-docx")
    sub = parser.add_subparsers(dest="command", required=True)

    inspect_parser = sub.add_parser("inspect")
    inspect_parser.add_argument("docx", type=Path)

    repair_parser = sub.add_parser("repair")
    repair_parser.add_argument("source", type=Path)
    repair_parser.add_argument("target", type=Path)
    repair_parser.add_argument("--east-asia", default="\u5b8b\u4f53")

    args = parser.parse_args()
    if args.command == "inspect":
        print(json.dumps(inspect_docx(args.docx), ensure_ascii=False, indent=2))
        return
    if args.command == "repair":
        print(json.dumps(repair_docx(args.source, args.target, args.east_asia), ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
