# Word Count Conventions

**Spec:** v3.6.7 搂7.1 鈥?pattern protection reference for `report_compiler_agent` (abstract-only mode).

# REDACTED: sensitive-looking memory line

**Why this exists:** Different word-count algorithms produce different totals on the same text. The differential is small per sentence but compounds: on a 250-word abstract, the choice between whitespace-split and hyphenated-as-1 can swing the total by ~12 words. An agent that uses a different algorithm than the publisher believes it is meeting the cap when it is over by 5%. This reference fixes a single canonical algorithm for ARS pipelines, documents how publishers diverge, and specifies the buffer rule that makes minor publisher variation safe.

---

## The canonical algorithm: whitespace-split

# REDACTED: sensitive-looking memory line

### Why whitespace-split

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
4. **Language-neutral.** CJK text without spaces is a separate problem (see "Non-space-delimited languages" below), but for English / European languages, whitespace-split is the universal lower bound.

### What whitespace-split counts

# REDACTED: sensitive-looking memory line
|---|---|
| `state-of-the-art` | 1 |
| `2020-2024` | 1 |
| `Smith, John-Paul` | 2 (`Smith,` and `John-Paul`) |
| `e.g.,` | 1 |
| `123,456` | 1 |
| `(n=42)` | 1 |
| `https://example.org/path` | 1 |

### What whitespace-split does NOT count

# REDACTED: sensitive-looking memory line
- Empty strings between consecutive whitespace characters are filtered by `split()` with no argument.
# REDACTED: sensitive-looking memory line

---

## Publisher conventions and how to adapt

# REDACTED: sensitive-looking memory line

### Common publisher families

| Publisher / venue | Stated algorithm | Practical effect |
|---|---|---|
| Springer / Nature | whitespace-equivalent for abstract, no explicit definition | matches ARS canonical |
| IEEE | "approximately N words" 鈥?whitespace-equivalent in their submission tool | matches ARS canonical |
| ACM | whitespace-equivalent in CCS submission | matches ARS canonical |
| Elsevier (Cell, Lancet families) | whitespace-equivalent in EM submission | matches ARS canonical |
| Wiley | whitespace-equivalent | matches ARS canonical |
| arXiv | no hard cap on abstract; advisory ~250 words | guideline only |
| ICLR / NeurIPS / ACL workshop tracks | hyphenated-as-1 in their LaTeX `\abstract{}` counter | matches ARS canonical |
| Some social-science journals (variable) | "page-based" 鈥?abstract must fit visually on submission template | not a true word count; check template |

### When the publisher uses a stricter algorithm

Some non-English-medium publishers and a small number of style guides count hyphenated compounds as multiple words. If the publisher explicitly states "hyphenated words count as separate words":

1. Calibration should compute both totals: `len(body.split())` and the hyphenated-as-N variant.
2. The dispatch context to the abstract compiler should carry both numbers.
3. The compiler should use the stricter (higher) total when budgeting.

If the publisher's algorithm is ambiguous, default to ARS canonical (whitespace-split) plus the 3鈥?% buffer.

---

## The 3鈥?% buffer rule

ARS pipelines reserve **3鈥?% below the publisher's stated hard cap** as buffer. For a 250-word abstract:

- 3% buffer 鈫?target 242 words
- 5% buffer 鈫?target 237 words

### Why this range

1. **Algorithm divergence absorbs into the buffer.** Even if the publisher's tool counts ~3% higher than `len(body.split())`, the abstract still meets the cap.
2. **Editor-side trimming room.** Reviewers and copy editors occasionally request a phrase change that adds 2鈥? words. Abstract that lands at exactly the cap forces a downstream cut; abstract that lands at cap minus 5% accommodates the change without cut.
3. **Title plus abstract pages.** Some publishers count the running title or running header; the buffer absorbs that too.

### When to use 3% vs. 5%

- **3%** when the calibration's `protected_hedges` block is large (鈮?0% of cap word budget). Tighter buffer keeps room for substantive content.
- **5%** when the publisher's algorithm is unstated or the protected hedges are minimal. Looser buffer absorbs more uncertainty.

### When NOT to use buffer

If the publisher imposes a strict character count instead of word count (rare, but happens with some Asian-language journals), the buffer rule does not apply directly. Calibration should compute character count under the publisher's stated encoding and apply a 1鈥?% buffer at the character level.

---

## Non-space-delimited languages

Mandarin, Japanese, Korean, Thai, and Lao do not delimit words with whitespace. ARS canonical algorithm produces meaningless totals on these texts.

For abstracts in non-space-delimited languages:

1. Use **character count**, not word count. Most publishers serving these languages specify character caps (e.g., Mandarin abstract often capped at 300 or 500 characters).
2. Apply 1鈥?% buffer at the character level.
3. The dispatch context to the abstract compiler should carry both `cap_unit: "character"` and the character cap, so the compiler does not erroneously apply word-budget logic.

# REDACTED: sensitive-looking memory line

---

## Where this convention is enforced

# REDACTED: sensitive-looking memory line

---

## Cross-references

- `shared/references/protected_hedging_phrases.md` 鈥?protected hedging phrases share the abstract budget; budget allocation order specified there.
- `shared/templates/codex_audit_multifile_template.md` 鈥?audit dimensions including word-count verification.
- ARS feedback memory `feedback_word_count_convention_mismatch.md` 鈥?original empirical observation of whitespace-split vs. hyphenated-as-1 differential (~12 words on a 250-word abstract).
