from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from chinese_docx.inspect import inspect_docx
from chinese_docx.openxml import NS, read_xml_part, w_attr
from chinese_docx.repair import repair_docx
from tests.fixtures.build_fixtures import SIMSUN, make_docx_missing_east_asia, make_docx_with_east_asia


def test_repair_adds_east_asia_to_cjk_runs(tmp_path: Path) -> None:
    source = tmp_path / "missing.docx"
    target = tmp_path / "repaired.docx"
    make_docx_missing_east_asia(source)

    result = repair_docx(source, target, east_asia_font=SIMSUN)

    assert result["runs_repaired"] >= 1
    assert inspect_docx(target)["summary"]["cjk_runs_missing_east_asia"] == 0


def test_repair_preserves_existing_east_asia(tmp_path: Path) -> None:
    source = tmp_path / "ok.docx"
    target = tmp_path / "repaired.docx"
    make_docx_with_east_asia(source)

    repair_docx(source, target, east_asia_font="\u5fae\u8f6f\u96c5\u9ed1")

    part = read_xml_part(target, "word/document.xml")
    assert part is not None
    rfonts = part.tree.xpath("//w:rFonts", namespaces=NS)[0]
    assert rfonts.get(w_attr("eastAsia")) == SIMSUN


def test_cli_inspect_outputs_json(tmp_path: Path) -> None:
    source = tmp_path / "missing.docx"
    make_docx_missing_east_asia(source)
    project_root = Path(__file__).parents[1]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "tools")

    result = subprocess.run(
        [sys.executable, "-m", "chinese_docx.cli", "inspect", str(source)],
        cwd=project_root,
        env=env,
        text=True,
        capture_output=True,
        check=True,
    )

    payload = json.loads(result.stdout)
    assert payload["summary"]["cjk_runs_missing_east_asia"] >= 1
