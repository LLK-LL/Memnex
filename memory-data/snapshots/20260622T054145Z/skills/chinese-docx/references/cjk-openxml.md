# CJK OpenXML Rules

Word stores run fonts in `w:rFonts`.

- `w:ascii`: Latin ASCII characters.
- `w:hAnsi`: high ANSI Latin text.
- `w:eastAsia`: Chinese, Japanese, and Korean characters.
- `w:cs`: complex script.

For Chinese text, `w:eastAsia` is the required slot. If a run contains Chinese text and only has `w:ascii="Times New Roman"`, Word may render Chinese through fallback fonts or square glyphs. A repair tool should add `w:eastAsia` without deleting `w:ascii` or `w:hAnsi`.

Common failure modes:

- Chinese becomes squares: `w:eastAsia` references a font not installed on the machine, or the slot is missing and fallback fails.
- Chinese font setting appears ignored: code only set `run.font.name`, which often maps to Latin font slots.
- Template format disappears: generator replaced styles with direct formatting or created a blank document instead of using the template.

Repair rule:

- Preserve existing `w:eastAsia`.
- Add fallback `w:eastAsia` only for runs containing CJK text or styles with Latin font slots but no CJK slot.
- Keep Latin slots unchanged unless the user explicitly asks to alter Latin typography.
