# IRB Terminology Glossary

**Spec:** v3.6.7 搂7.1 鈥?pattern protection reference for `research_architect_agent` (survey designer mode), Pattern B1.

# REDACTED: sensitive-looking memory line

**Why this exists:** In live ARS pipeline runs, survey instrument drafts repeatedly conflated four IRB terms that look adjacent in everyday English but carry distinct operational commitments. Conflation creates legal-effect drift in the consent script and can make the instrument unenforceable as informed consent. This reference is the canonical distinction the survey designer must pass through.

---

## The four terms

The four terms differ along two axes: (1) what is hidden 鈥?identity vs. content 鈥?and (2) whether re-identification is technically possible.

### Anonymity

**Operational definition:** The respondent's identity cannot be linked to their response by anyone, including the researcher. No identity key is created or stored.

**Necessary conditions:**
- No name, email, IP, device fingerprint, or directly-identifying field is collected.
# REDACTED: sensitive-looking memory line
- Demographic combinations are coarse enough that no respondent is uniquely identifiable from the demographic combination alone (k-anonymity 鈮?k for some agreed k, typically k 鈮?5).

**Example consent phrasing (correct):**
> "Your responses are anonymous. We do not collect your name, email, or any identifier that could link this survey to you. We cannot contact you about your responses, and we cannot remove your responses from the dataset after submission because we cannot identify which responses are yours."

**Common drift to flag:**
- Claiming "anonymous" while collecting email "for follow-up" 鈥?that is **confidential**, not anonymous.
- Claiming "anonymous" while assigning a respondent code that the researcher holds 鈥?that is **pseudonymous**, not anonymous.

### Confidentiality

**Operational definition:** The respondent's identity IS known to the researcher, but the researcher commits not to disclose it. Identity-response linkage exists in the research record.

**Necessary conditions:**
- A written commitment specifies who can see the identified data, for what purpose, and for how long.
- Storage and access controls match the commitment (encrypted at rest, access-logged, retention-bounded).
- Reporting layer aggregates or de-identifies before any external disclosure.

**Example consent phrasing (correct):**
> "Your responses are confidential. We will know your identity from the email you provide for follow-up. Your name will not appear in any report. Only the named research team will see identified data, and identified data will be deleted within 12 months of project close."

**Common drift to flag:**
- Promising "confidentiality" without specifying a retention boundary 鈥?IRB will reject; respondent cannot evaluate the commitment.
- Promising "confidentiality" while planning to publish identifiable case-study quotes 鈥?that is a contradiction; either the consent script needs an explicit case-study clause or the publication plan needs aggregation.

### De-identification

**Operational definition:** Direct identifiers have been removed from a dataset, and the link key created during data collection has been destroyed. The remaining record cannot be re-linked to the respondent.

**Necessary conditions:**
- Direct identifiers (HIPAA Safe Harbor's 18 fields or the project's equivalent list) are removed or transformed into non-reversible categories.
- Quasi-identifiers (zip + birth-date + gender, etc.) are evaluated for re-identification risk against plausible auxiliary datasets and reduced to acceptable risk threshold.
- The link key used during data collection is **destroyed**. Any retained re-link key 鈥?even one held by an independent custodian 鈥?falls under pseudonymization (next section), not de-identification, because re-identification remains technically possible.

**Example dataset description (correct):**
> "The released dataset is de-identified. Names, emails, exact dates, and institutional affiliation have been removed. Birth year is generalised to 5-year buckets. The collection-time link key was destroyed at the close of data collection."

**Common drift to flag:**
- Claiming "de-identified" while keeping the link key for "potential follow-up" 鈥?that is **pseudonymized**, not de-identified.
- Claiming "de-identified" without a quasi-identifier risk evaluation 鈥?k-anonymity unverified.

### Pseudonymization

# REDACTED: sensitive-looking memory line

**Necessary conditions:**
- A documented pseudonymization scheme specifies the substitution method and the link-key custodian.
- The link key is held separately from the pseudonymized dataset, with separate access controls.
- Use cases (longitudinal follow-up, data subject access request, error correction) are pre-specified.

**Example dataset description (correct):**
> "The dataset is pseudonymized. Each participant is assigned an opaque code (e.g., P-0042). The mapping from code to participant identity is held by the principal investigator and is not shared with the analytic team. The mapping is retained for 24 months to support follow-up surveys, then destroyed."

**Common drift to flag:**
- Calling pseudonymized data "anonymized" 鈥?under GDPR, EU AI Act, and most modern IRB guidance, pseudonymized data remains personal data subject to the full data protection regime.

---

## Quick distinction table

| Term | Identity-response link exists? | Held by whom? | Reversible? |
|---|---|---|---|
| **Anonymity** | No | N/A | No |
| **Confidentiality** | Yes | Researcher | Yes (within research team) |
| **De-identification** | No (key destroyed) | N/A | No (assuming key destroyed and quasi-identifier risk acceptable) |
| **Pseudonymization** | Yes (via key) | Researcher / data controller | Yes |

---

## Where this glossary is enforced

# REDACTED: sensitive-looking memory line

---

## References

- HHS HIPAA Safe Harbor de-identification (45 CFR 164.514(b)(2)) 鈥?primary source for direct-identifier list.
- GDPR Art. 4(5) 鈥?pseudonymization definition.
- EU AI Act Recital 27 + Art. 10(5) 鈥?pseudonymization vs. anonymization distinction in AI training contexts.
- ISO/IEC 27559:2022 鈥?privacy-enhancing data de-identification framework.
