from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from lxml import etree

from chinese_docx.openxml import NS, read_xml_part, w_attr

CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def contains_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def _run_text(run: etree._Element) -> str:
    return "".join(run.xpath(".//w:t/text()", namespaces=NS))


def _run_has_east_asia(run: etree._Element) -> bool:
    rfonts = run.find("./w:rPr/w:rFonts", namespaces=NS)
    return rfonts is not None and bool(rfonts.get(w_attr("eastAsia")))


def _style_reports(docx_path: Path) -> list[dict[str, Any]]:
    part = read_xml_part(docx_path, "word/styles.xml")
    if part is None:
        return []
    rows: list[dict[str, Any]] = []
    for style in part.tree.xpath("//w:style", namespaces=NS):
        style_id = style.get(w_attr("styleId"), "")
        name_el = style.find("./w:name", namespaces=NS)
        rfonts = style.find("./w:rPr/w:rFonts", namespaces=NS)
        rows.append(
            {
                "style_id": style_id,
                "name": name_el.get(w_attr("val")) if name_el is not None else style_id,
                "ascii": rfonts.get(w_attr("ascii")) if rfonts is not None else None,
                "hAnsi": rfonts.get(w_attr("hAnsi")) if rfonts is not None else None,
                "eastAsia": rfonts.get(w_attr("eastAsia")) if rfonts is not None else None,
            }
        )
    return rows


def inspect_docx(docx_path: Path) -> dict[str, Any]:
    document = read_xml_part(docx_path, "word/document.xml")
    missing_runs: list[dict[str, Any]] = []
    if document is not None:
        for index, run in enumerate(document.tree.xpath("//w:r", namespaces=NS)):
            text = _run_text(run)
            if text and contains_cjk(text) and not _run_has_east_asia(run):
                missing_runs.append({"run_index": index, "text": text})

    styles = _style_reports(docx_path)
    styles_missing = [style for style in styles if style["ascii"] and not style["eastAsia"]]
    return {
        "summary": {
            "cjk_runs_missing_east_asia": len(missing_runs),
            "styles_missing_east_asia": len(styles_missing),
        },
        "cjk_runs_missing_east_asia": missing_runs,
        "styles_missing_east_asia": styles_missing,
        "styles": styles,
    }
