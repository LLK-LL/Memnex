---
name: chinese-docx
description: Use when creating, inspecting, repairing, or converting Chinese Word DOCX files, especially when Chinese fonts render as squares, template formatting is lost, Markdown is converted to Word, or CJK typography matters.
---

# Chinese DOCX Skill

## Trigger

Use this skill for Chinese Word documents, DOCX template generation, Markdown-to-Word delivery, CJK font problems, square glyphs, garbled Chinese, style loss, page layout repair, thesis/report formatting, and template inspection.

## Core Rule

Chinese font control requires `w:rFonts w:eastAsia`. Setting only `w:ascii` or `w:hAnsi` is not enough for Chinese characters.

## Workflow

1. If a template exists, inspect the template before generating output.
2. Preserve template styles by default.
3. Only fill missing CJK font slots; do not overwrite existing `w:eastAsia`.
4. After generation, inspect the output DOCX.
5. If CJK runs or styles are missing `w:eastAsia`, repair the DOCX and inspect again.

## Commands

Run commands from this skill directory. If the package is not installed, set `PYTHONPATH=tools` first.

PowerShell inspect:

```powershell
$env:PYTHONPATH = "tools"
python -m chinese_docx.cli inspect input.docx
```

PowerShell repair:

```powershell
$env:PYTHONPATH = "tools"
python -m chinese_docx.cli repair input.docx output.docx --east-asia SimSun
```

Installed package inspect:

```bash
chinese-docx inspect input.docx
```

Installed package repair:

```bash
chinese-docx repair input.docx output.docx --east-asia SimSun
```

## Default Font Policy

- Body Chinese: SimSun. Chinese display name: U+5B8B U+4F53.
- Heading Chinese: SimHei. Chinese display name: U+9ED1 U+4F53.
- Modern screen-oriented report heading: Microsoft YaHei.
- Latin body: Times New Roman.
- Never assume a font is installed on the recipient machine; prefer common Windows Chinese fonts for deliverables.

## Template Policy

# REDACTED: sensitive-looking memory line

## References

- `references/cjk-openxml.md`
- `references/template-first.md`
