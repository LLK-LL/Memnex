from __future__ import annotations

from pathlib import Path

from chinese_docx.inspect import inspect_docx
from tests.fixtures.build_fixtures import CJK_SAMPLE, make_docx_missing_east_asia, make_docx_with_east_asia


def test_inspect_reports_missing_east_asia_for_cjk_runs(tmp_path: Path) -> None:
    docx = tmp_path / "missing.docx"
    make_docx_missing_east_asia(docx)

    report = inspect_docx(docx)

    assert report["summary"]["cjk_runs_missing_east_asia"] >= 1
    assert any(item["text"] == CJK_SAMPLE for item in report["cjk_runs_missing_east_asia"])


def test_inspect_does_not_flag_runs_with_east_asia(tmp_path: Path) -> None:
    docx = tmp_path / "ok.docx"
    make_docx_with_east_asia(docx)

    report = inspect_docx(docx)

    assert report["summary"]["cjk_runs_missing_east_asia"] == 0
