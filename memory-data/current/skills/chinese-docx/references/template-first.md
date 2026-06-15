# Template-First Rules

Templates are authoritative. Treat the template as the style contract.

Required behavior:

- Inspect template styles before writing content.
- Reuse existing paragraph and character styles.
- Preserve existing `w:eastAsia` values.
- Add a fallback `w:eastAsia` only when the style or run lacks one.
- Do not flatten all content into direct formatting.

Recommended flow:

1. Inspect `template.docx`.
2. Generate or convert content using the template.
3. Inspect the generated DOCX.
4. Repair missing CJK font slots.
5. Reinspect and include the report with the deliverable.

When generated output looks wrong, diagnose in this order:

1. Check whether the content used the template at all.
2. Check whether the affected style has `w:eastAsia`.
3. Check whether direct runs override style font settings.
4. Check whether the requested Chinese font exists on the viewing machine.
