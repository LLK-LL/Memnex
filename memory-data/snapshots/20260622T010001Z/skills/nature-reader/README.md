# nature-reader

Markdown-first reading workflow for full papers.

## What it does

`nature-reader` turns a PDF, DOI, arXiv link, publisher HTML page, or pasted manuscript into a complete Markdown reading artifact with:

- paragraph-level original text and Chinese translation in prose form
- extracted figures and tables placed near the discussion that first substantively references them
- original captions plus Chinese caption translations
- stable page and block anchors for traceability
- tight figure crops and a full-document source map

## Primary outputs

- `paper.md`
- `source_map.json`
- `translation_notes.md`
- `assets/`

`reader.html` can be generated as a secondary preview, but the skill is Markdown-first and does not default to an interactive Q&A panel.

## Trigger phrases

Use this skill when the user asks for:

- full-paper translation
- 鍘熸枃瀵圭収
- 涓嫳鏂囧鐓?
- 鍥炬枃瀵瑰簲
- 鍥捐〃鎻愬彇
- 缈昏瘧瑙ｈ
- 鍏ㄦ枃 Markdown
- paper md
- source-grounded reading notes

## Notes

Do not use this skill for summaries, keyword bullets, or citation-only search tasks.
When triggered, do not output only a Chinese summary. The default artifact is `paper.md` with visible `Original` / `涓枃` pairs and figure/table cards inserted at the relevant source locations.
