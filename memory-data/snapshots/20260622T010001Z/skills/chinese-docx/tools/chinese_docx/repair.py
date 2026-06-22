from __future__ import annotations

from pathlib import Path
from typing import Any

from lxml import etree

from chinese_docx.inspect import contains_cjk
from chinese_docx.openxml import NS, read_xml_part, w_attr, write_docx_with_parts


def _ensure_child(parent: etree._Element, tag: str) -> etree._Element:
    child = parent.find(tag, namespaces=NS)
    if child is not None:
        return child
    local_name = tag.split(":")[1]
    child = etree.Element(w_attr(local_name))
    parent.insert(0, child)
    return child


def _text(run: etree._Element) -> str:
    return "".join(run.xpath(".//w:t/text()", namespaces=NS))


def _repair_runs(tree: etree._ElementTree, east_asia_font: str) -> int:
    count = 0
    for run in tree.xpath("//w:r", namespaces=NS):
        if not contains_cjk(_text(run)):
            continue
        rpr = _ensure_child(run, "w:rPr")
        rfonts = _ensure_child(rpr, "w:rFonts")
        if not rfonts.get(w_attr("eastAsia")):
            rfonts.set(w_attr("eastAsia"), east_asia_font)
            count += 1
    return count


def _repair_styles(tree: etree._ElementTree, east_asia_font: str) -> int:
    count = 0
    for style in tree.xpath("//w:style[w:rPr/w:rFonts]", namespaces=NS):
        rfonts = style.find("./w:rPr/w:rFonts", namespaces=NS)
        if rfonts is not None and rfonts.get(w_attr("ascii")) and not rfonts.get(w_attr("eastAsia")):
            rfonts.set(w_attr("eastAsia"), east_asia_font)
            count += 1
    return count


def repair_docx(source: Path, target: Path, east_asia_font: str = "\u5b8b\u4f53") -> dict[str, Any]:
    changed_parts: dict[str, etree._ElementTree] = {}
    runs_repaired = 0
    styles_repaired = 0

    document = read_xml_part(source, "word/document.xml")
    if document is not None:
        runs_repaired = _repair_runs(document.tree, east_asia_font)
        changed_parts[document.name] = document.tree

    styles = read_xml_part(source, "word/styles.xml")
    if styles is not None:
        styles_repaired = _repair_styles(styles.tree, east_asia_font)
        changed_parts[styles.name] = styles.tree

    write_docx_with_parts(source, target, changed_parts)
    return {"runs_repaired": runs_repaired, "styles_repaired": styles_repaired}
