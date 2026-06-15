# Task: LaTeX Compilation and Bug Fixing

After every substantive edit to a `.tex` file, compile the document and fix all errors before reporting completion.

## Compilation Workflow

```bash
pdflatex -interaction=nonstopmode main.tex
bibtex main          # only if bibliography was modified
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Adjust `main.tex` to match the actual root file of the project.

## Error-Fixing Loop

1. Read the `.log` file to locate the first `!` error.
2. Fix that error in the source.
3. Recompile.
4. Repeat until the exit code is 0 and the log contains no `!` errors.

Do not mark a task complete until compilation succeeds.

## Common Errors and Fixes

| Error | Fix |
|---|---|
| Undefined citation key | Add or correct the entry in the `.bib` file |
| Missing `\end{...}` | Find and close the unclosed environment |
| Unescaped special character | Escape `&` `%` `$` `#` `_` `^` `{` `}` `~` `\` in plain text |
| Font or encoding issue | Check preamble for correct package (`inputenc`, `fontenc`, etc.) |
| Overfull/underfull hbox (severe) | Adjust line breaks, hyphenation, or column widths |
