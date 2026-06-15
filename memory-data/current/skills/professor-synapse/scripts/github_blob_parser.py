#!/usr/bin/env python3
"""
github_blob_parser.py
Parses GitHub blob page HTML and extracts file content as clean Markdown.
Used by fetch-github-file.sh
"""

import sys
import json
import re

def convert_frontmatter_table_to_yaml(markdown):
    """
    GitHub renders YAML frontmatter as an HTML table.
    This converts the resulting markdown table back to YAML frontmatter.

    GitHub's layout is 2-column vertical (key in col 0, value in col 1),
    where the first key/value pair is embedded in the header row:

        name | professor-synapse
        ---|---
        description | Use when ...
        tags | foo, bar

    Converts to:
        ---
        name: professor-synapse
        description: Use when ...
        tags: foo, bar
        ---
    """
    lines = markdown.split('\n')

    # Need at least 3 lines for a frontmatter table
    if len(lines) < 3:
        return markdown

    def split_row(line):
        # Trim trailing markdown hard-break ("  ") and leading/trailing pipes
        parts = [p.strip() for p in line.strip().rstrip('|').lstrip('|').split('|')]
        return [p for p in parts if p != '']

    # First row must have exactly 2 cells (key | value)
    first = split_row(lines[0])
    if len(first) != 2:
        return markdown

    # Separator must be second line: ---|---
    sep = lines[1].strip()
    if not re.match(r'^[\s\-|]+$', sep) or '|' not in sep:
        return markdown

    # Validate that at least one plausible frontmatter key is present
    frontmatter_keys = {'name', 'description', 'title', 'author', 'date', 'tags',
                        'license', 'version', 'compatibility'}

    pairs = [(first[0], first[1])]
    end_index = 2

    # Consume additional 2-column rows until we hit a non-table line
    for i in range(2, len(lines)):
        row_text = lines[i].strip()
        if row_text == '' or row_text.replace(' ', '') == '':
            end_index = i
            break
        cells = split_row(lines[i])
        if len(cells) != 2:
            end_index = i
            break
        pairs.append((cells[0], cells[1]))
        end_index = i + 1

    # Require at least one recognized frontmatter key to avoid false positives
    if not any(k.lower() in frontmatter_keys for k, _ in pairs):
        return markdown

    # Build YAML frontmatter
    yaml_lines = ['---']
    for key, value in pairs:
        if '\n' in value or ':' in value or value.startswith('['):
            escaped = value.replace('"', '\\"')
            yaml_lines.append(f'{key}: "{escaped}"')
        else:
            yaml_lines.append(f'{key}: {value}')
    yaml_lines.append('---')
    yaml_lines.append('')

    rest_of_doc = '\n'.join(lines[end_index:]).lstrip('\n')
    return '\n'.join(yaml_lines) + rest_of_doc

def main():
    content = sys.stdin.read()

    # Find embedded JSON data
    match = re.search(
        r'<script type="application/json" data-target="react-app\.embeddedData">(.*?)</script>',
        content,
        re.DOTALL
    )
    if not match:
        print('Error: Could not find embedded data in GitHub page', file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(match.group(1))
        payload = data.get('payload', {})
        # New GitHub structure (2025+): data split across routes
        # Markdown rich text lives in codeViewBlobRoute
        # Raw lines for non-markdown live in codeViewBlobLayoutRoute.StyledBlob
        blob = (
            payload.get('codeViewBlobRoute')
            or payload.get('blob')
            or {}
        )
        styled_blob = (
            payload.get('codeViewBlobLayoutRoute.StyledBlob')
            or payload.get('codeViewBlobLayoutRoute', {}).get('blob')
            or {}
        )
        rich_text = blob.get('richText') or ''

        if not rich_text:
            # Try rawLines for non-markdown files (scripts, etc.)
            raw_lines = (
                styled_blob.get('rawLines')
                or blob.get('rawLines')
            )
            if raw_lines:
                print('\n'.join(raw_lines))
                sys.exit(0)
            print('Error: No content found in blob', file=sys.stderr)
            sys.exit(1)

        # Convert HTML to Markdown
        try:
            import html2text
        except ImportError:
            print('Error: html2text not installed. Run: pip install html2text', file=sys.stderr)
            sys.exit(1)

        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = True
        h.body_width = 0
        h.unicode_snob = True

        markdown = h.handle(rich_text)

        # === POST-PROCESSING FOR CLEANER OUTPUT ===

        # Fix YAML frontmatter that was rendered as a table
        markdown = convert_frontmatter_table_to_yaml(markdown)

        # Fix horizontal rules: '* * *' -> '---'
        markdown = re.sub(r'^\* \* \*$', '---', markdown, flags=re.MULTILINE)

        # Fix escaped hyphens: '\-' -> '-'
        markdown = re.sub(r'\\-', '-', markdown)

        # Fix spaces before punctuation after bold/italic: '**text** ,' -> '**text**,'
        markdown = re.sub(r'\*\*([^*]+)\*\* ([,.:;!?])', r'**\1**\2', markdown)
        markdown = re.sub(r'\*([^*]+)\* ([,.:;!?])', r'*\1*\2', markdown)

        # Fix spaces after bold at start of definitions: '**Triggers** :' -> '**Triggers**:'
        markdown = re.sub(r'\*\*([^*]+)\*\* :', r'**\1**:', markdown)

        # Fix extra spaces after bold/italic
        markdown = re.sub(r'\*\*([^*]+)\*\*  +', r'**\1** ', markdown)

        # Convert indented code blocks to fenced code blocks
        lines = markdown.split('\n')
        in_code_block = False
        result_lines = []
        code_buffer = []

        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.lstrip()
            indent = len(line) - len(stripped)

            if not in_code_block:
                if indent >= 4 and stripped:
                    is_code_block = False
                    if i + 1 < len(lines):
                        next_line = lines[i + 1]
                        next_stripped = next_line.lstrip()
                        next_indent = len(next_line) - len(next_stripped)
                        if next_indent >= 4 or next_line.strip() == '':
                            is_code_block = True

                    if is_code_block:
                        in_code_block = True
                        result_lines.append('```')
                        code_buffer.append(line[4:])
                    else:
                        result_lines.append(line)
                else:
                    result_lines.append(line)
            else:
                if indent >= 4 or line.strip() == '':
                    if line.strip() == '':
                        code_buffer.append('')
                    else:
                        code_buffer.append(line[4:])
                else:
                    while code_buffer and code_buffer[-1] == '':
                        code_buffer.pop()
                    result_lines.extend(code_buffer)
                    result_lines.append('```')
                    code_buffer = []
                    in_code_block = False
                    result_lines.append(line)

            i += 1

        if in_code_block:
            while code_buffer and code_buffer[-1] == '':
                code_buffer.pop()
            result_lines.extend(code_buffer)
            result_lines.append('```')

        markdown = '\n'.join(result_lines)

        # Clean up excessive blank lines (3+ -> 2)
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

        # Remove trailing whitespace from lines
        markdown = '\n'.join(line.rstrip() for line in markdown.split('\n'))

        # Ensure file ends with single newline
        markdown = markdown.strip() + '\n'

        print(markdown, end='')

    except json.JSONDecodeError as e:
        print(f'Error: Failed to parse JSON: {e}', file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
