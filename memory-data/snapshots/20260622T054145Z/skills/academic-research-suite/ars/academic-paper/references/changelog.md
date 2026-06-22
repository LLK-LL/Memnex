# Version History

| Version | Date | Changes |
|---------|------|---------|
# REDACTED: sensitive-looking memory line
| 2.4 | 2026-03-08 | LaTeX output formatting hardening: mandatory `apa7` document class for APA 7.0 output; text justification fix (`ragged2e` + `etoolbox` to override apa7 man mode `\raggedright`); table column width formula (`(\linewidth - N\tabcolsep) * \real{proportion}` 鈥?prevents overflow); bilingual abstract centering (`\begin{center}\textbf{...}\end{center}`); font stack standardized (Times New Roman + Source Han Serif TC VF + Courier New); `xurl` for URL line breaking; `fancyvrb` Verbatim with `fontsize` for wide content; PDF must compile from LaTeX via tectonic (no HTML-to-PDF) |
| 2.3 | 2026-03-08 | NEW visualization_agent (11th: publication-quality figures with matplotlib/ggplot2, APA 7.0, colorblind-safe); NEW revision_coach_agent (12th: standalone reviewer comment parser 鈫?Revision Roadmap); Socratic convergence criteria (4 signals: thesis clarity, chapter coherence, evidence mapping, limitation honesty) + question taxonomy (clarifying, probing, structuring, challenging); revision tracking template (4 status types); citation format conversion in formatter_agent (APA 7 鈫?Chicago 鈫?MLA 鈫?IEEE 鈫?Vancouver); Quick Mode Selection Guide; 9th mode: revision-coach |
| 2.2 | 2026-03-05 | 4-level argument strength scoring with quantified thresholds; plagiarism & retraction screening protocol; F11 Desk-Reject Recovery + F12 Conference-to-Journal Conversion failure paths; Plan -> Full mode conversion protocol; cross-skill reference to `shared/handoff_schemas.md` |
# REDACTED: sensitive-looking memory line
| 2.0 | 2026-02 | NEW plan mode (Socratic guided chapter-by-chapter planning), deep-research handoff protocol, Chinese APA 7.0 citation guide, failure path handling, mode selection guide |
| 1.0 | 2026-01 | Initial release: 9-agent pipeline, 6 paper types, 5 citation formats, bilingual abstracts, multi-format output |
