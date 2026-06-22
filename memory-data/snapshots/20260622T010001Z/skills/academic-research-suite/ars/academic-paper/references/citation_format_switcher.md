# Citation Format Switcher 鈥?Multi-Citation Format Switching

Quick-reference for switching between 5 citation formats. Used by `citation_compliance_agent` and `formatter_agent`.

## Format Comparison Matrix

### In-Text Citation Patterns

# REDACTED: sensitive-looking memory line
|----------|---------|-----------------|----------------------|---------|------|-----------|
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
| Direct quote | (Smith, 2024, p. 45) | 鹿 | (Smith 2024, 45) | (Smith 45) | [1, p. 45] | 鹿鈦结禆鈦粹伒鈦?|
| Multiple works | (Chen, 2023; Smith, 2024) | 鹿 虏 | (Chen 2023; Smith 2024) | (Chen 12; Smith 45) | [1], [2] | 鹿藪虏 |
| Order | Alphabetical | Order of appearance | Alphabetical | Alphabetical | Order of appearance | Order of appearance |

### Reference List Naming

| Format | Section Title | Entry Order |
|--------|--------------|-------------|
| APA 7th | References | Alphabetical |
| Chicago (Notes) | Bibliography | Alphabetical |
# REDACTED: sensitive-looking memory line
| MLA 9th | Works Cited | Alphabetical |
| IEEE | References | Order of appearance |
| Vancouver | References | Order of appearance |

## Format Details

### APA 7th Edition
**Discipline**: Education, Psychology, Social Sciences

**Journal Article**:
```
Smith, J. A., & Jones, B. C. (2024). Article title in sentence case.
    Journal Title in Title Case, 45(2), 123-145. https://doi.org/10.xxxx
```

**Book**:
```
Smith, J. A. (2024). Book title in sentence case (2nd ed.). Publisher.
```

# REDACTED: sensitive-looking memory line

---

### Chicago 17th (Notes-Bibliography)
**Discipline**: History, Humanities, some Social Sciences

**Footnote (first citation)**:
```
1. John A. Smith and Betty C. Jones, "Article Title in Title Case,"
Journal Title 45, no. 2 (2024): 123, https://doi.org/10.xxxx.
```

**Footnote (subsequent)**:
```
2. Smith and Jones, "Article Title," 130.
```

**Bibliography entry**:
```
Smith, John A., and Betty C. Jones. "Article Title in Title Case."
    Journal Title 45, no. 2 (2024): 123-145.
    https://doi.org/10.xxxx.
```

**Key rules**: Full names, title case throughout, footnotes + bibliography, period after URL.

---

# REDACTED: sensitive-looking memory line
**Discipline**: Natural Sciences, some Social Sciences

**In-text**: (Smith 2024, 45)

**Reference**:
```
Smith, John A. 2024. "Article Title in Title Case." Journal Title
    45 (2): 123-145. https://doi.org/10.xxxx.
```

# REDACTED: sensitive-looking memory line

---

### MLA 9th Edition
**Discipline**: Literature, Languages, Cultural Studies

# REDACTED: sensitive-looking memory line

**Works Cited**:
```
Smith, John A., and Betty C. Jones. "Article Title in Title Case."
    Journal Title, vol. 45, no. 2, 2024, pp. 123-45.
```

**Key rules**: No year in in-text, page numbers always, containers model, no DOI in basic format (include if online), title case for all titles.

---

### IEEE
**Discipline**: Engineering, Computer Science, Technology

**In-text**: [1] 鈥?numbered brackets in order of appearance

**Reference**:
```
[1] J. A. Smith and B. C. Jones, "Article title in sentence case,"
    Journal Title, vol. 45, no. 2, pp. 123-145, Feb. 2024,
    doi: 10.xxxx.
```

**Key rules**: Numbered [N], initials before surname, abbreviated month, "doi:" prefix (not URL).

---

### Vancouver
**Discipline**: Medicine, Biomedical Sciences, Nursing

**In-text**: Superscript numbers 鹿 or (1) in order of appearance

**Reference**:
```
1. Smith JA, Jones BC. Article title in sentence case. Journal Title.
   2024;45(2):123-145. doi:10.xxxx
```

**Key rules**: Numbered in order of appearance, no spaces in initials, abbreviated journal titles (per NLM), semicolon before volume, colon before pages.

## Conversion Quick Reference

### APA 鈫?Chicago (Notes-Bibliography)
# REDACTED: sensitive-looking memory line
2. Expand first names in reference list
3. Change sentence case 鈫?title case for article titles
4. Add period after URLs
5. Rename "References" 鈫?"Bibliography"

### APA 鈫?MLA
1. Remove years from in-text, add page numbers
2. Expand first names, change "&" 鈫?"and"
3. Change format: vol., no., year order
4. Remove DOIs (unless online-only source)
5. Rename "References" 鈫?"Works Cited"

### APA 鈫?IEEE
# REDACTED: sensitive-looking memory line
2. Reorder references by appearance (not alphabetical)
3. Change to initials-first format
4. Add "doi:" prefix to DOIs
5. Abbreviate month names

### APA 鈫?Vancouver
# REDACTED: sensitive-looking memory line
2. Reorder references by appearance
3. Remove spaces between initials
4. Abbreviate journal titles (NLM catalog)
5. Use semicolons/colons for volume/page separators

## Chinese Citation Format Switching

### APA 7.0 Chinese Format

For complete specifications, see `apa7_chinese_citation_guide.md`. Below is a quick reference.

**Chinese journal article**:
```
Wang, Da-Ming, & Li, Xiao-Hua (2024). Article title. Journal Name, Volume(Issue), Pages. https://doi.org/xxxxx
```

**Chinese book**:
```
Zhang, San (2023). Book title. Publisher.
```

**Government publication**:
```
Ministry of Education (2024). Publication title. https://url
```

### Mixed Chinese-English Reference Handling

**In-text citations**:
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

**Reference list ordering**:

| Option | Description | Applicable Scenario |
|------|------|---------|
| **Option A (Recommended)** | Chinese first (ordered by stroke count), English after (ordered alphabetically) | Convention for most Taiwan journals |
| **Option B** | Mixed Chinese-English ordering (unified stroke count / alphabetical) | Some international journals |

# REDACTED: sensitive-looking memory line

### Format Conversion Notes (Chinese Papers)

**Chinese APA 鈫?Chicago**:
1. Publication format differs (APA 7 does not require publication location, Chicago does)
2. Change titles to "title case" format
3. Add footnote citation system

**Chinese APA 鈫?IEEE**:
1. Add numbered labels [N]
# REDACTED: sensitive-looking memory line
3. Order by citation appearance (not stroke count)

**Chinese paper format conventions**:
- Most Taiwan journals use APA
- Humanities disciplines (history, literature) occasionally use Chicago
- Engineering/CS fields mostly use IEEE
- Medical fields use Vancouver

---

## AI-Generated Content Citation (by Format)

| Format | How to Cite AI |
|--------|---------------|
| APA 7th | OpenAI. (2024). ChatGPT (Version 4) [Large language model]. https://chat.openai.com |
| Chicago | OpenAI. ChatGPT. Version 4. 2024. Large language model. https://chat.openai.com. |
| MLA | "ChatGPT response to [prompt description]." OpenAI, 15 Mar. 2024, chat.openai.com. |
| IEEE | [N] OpenAI, "ChatGPT," ver. 4, 2024. [Online]. Available: https://chat.openai.com |
| Vancouver | OpenAI. ChatGPT [Large language model]. 2024. Available from: https://chat.openai.com |
