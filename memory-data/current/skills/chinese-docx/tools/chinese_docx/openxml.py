from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}


def w_attr(name: str) -> str:
    return f"{{{W_NS}}}{name}"


@dataclass(frozen=True)
class DocxXmlPart:
    name: str
    tree: etree._ElementTree


def read_xml_part(docx_path: Path, part_name: str) -> DocxXmlPart | None:
    with ZipFile(docx_path, "r") as zin:
        if part_name not in zin.namelist():
            return None
        with zin.open(part_name) as handle:
            return DocxXmlPart(part_name, etree.parse(handle))


def write_docx_with_parts(source: Path, target: Path, parts: dict[str, etree._ElementTree]) -> None:
    with ZipFile(source, "r") as zin, ZipFile(target, "w", ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename in parts:
                data = etree.tostring(
                    parts[item.filename],
                    xml_declaration=True,
                    encoding="UTF-8",
                    standalone=True,
                )
            else:
                data = zin.read(item.filename)
            zout.writestr(item, data)
