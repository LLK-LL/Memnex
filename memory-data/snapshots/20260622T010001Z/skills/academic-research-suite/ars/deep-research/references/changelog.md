## [2.9.1] - 2026-04-22

### Added

- **Opt-in reading-check probe** in Socratic Mentor. Gated by `ARS_SOCRATIC_READING_PROBE=1`. See `agents/socratic_mentor_agent.md` 搂"Optional Reading Probe Layer" and `SKILL.md` 搂"Opt-in Reading Probe (v3.5.1)".

### Version

- 2.9.0 鈫?2.9.1 (patch; opt-in, default OFF).

---

# Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.4 | 2026-03-27 | Report compiler now consumes optional Style Profile (from academic-paper intake) and runs Writing Quality Check checklist before finalizing reports. Style Profile applied as soft guide for Executive Summary and Synthesis sections; discipline conventions take priority. Writing Quality Check catches overused AI-typical terms, em dash overuse, throat-clearing openers, and monotonous sentence rhythm. See `academic-paper/references/writing_quality_check.md` and `shared/style_calibration_protocol.md` |
# REDACTED: sensitive-looking memory line
| 2.2 | 2026-03-05 | Added synthesis anti-patterns, Socratic quantified thresholds & auto-end conditions, reference existence verification (DOI + WebSearch), enhanced ethics reference integrity check (50% + Retraction Watch), mode transition matrix, cross-agent quality alignment definitions |
| 2.1 | 2026-03 | Added IRB decision tree, EQUATOR reporting guidelines, preregistration guide + template; enhanced ethics_review_agent with human subjects dimension; enhanced research_architect_agent with ethics/EQUATOR/preregistration integration; enhanced methodology_patterns with EQUATOR cross-references |
| 2.0 | 2026-02 | Added socratic mode (10th agent), failure paths, mode selection guide, handoff protocol, 2 new examples, 3 new references |
| 1.0 | 2026-02 | Initial release: 9 agents, 5 modes, 6-phase pipeline |
