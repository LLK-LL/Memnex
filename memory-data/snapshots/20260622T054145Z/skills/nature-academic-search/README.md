# Academic Search

Claude Code 鐨勫鏈悳绱㈡妧鑳藉寘锛岄泦鎴?CrossRef銆丳ubMed銆乤rXiv銆丼copus銆丼cienceDirect 鏂囩尞鏁版嵁婧愩€?

## 鍔熻兘

- **澶氭簮骞跺彂鎼滅储**: 榛樿鏌ヨ CrossRef / PubMed / arXiv锛屽苟鍚堝苟杩斿洖缁撴灉
- **鎸?ID 鑾峰彇璇︽儏**: 鏀寔 DOI銆丳MID銆乤rXiv ID 鑷姩璇嗗埆
- **鏍煎紡鍖栧紩鐢?*: APA / Nature / IEEE / Vancouver 绛夐鏍?
- **MeSH 璇嶈〃鏌ヨ**: 鏋勫缓绮惧噯 PubMed 妫€绱㈠紡
- **鏂囩尞绠＄悊鑴氭湰**: .nbib / .ris / .bib / .enw 鏍煎紡浜掕浆
- **Scopus / ScienceDirect**: 鏀寔璁烘枃銆佷綔鑰呫€佹満鏋勩€佹湡鍒娿€佸紩鐢ㄦ瑙堛€丳lumX 鎸囨爣鍜?ScienceDirect 鍏冩暟鎹绱?

## MCP 杩愯

鎻掍欢榛樿閫氳繃 uv 鍚姩闅旂杩愯鐜锛?

```bash
uv run --no-project --directory <mcp-server> --with "mcp>=1.0.0,<2.0.0" --with "requests>=2.28.0,<3.0.0" --with "toml>=0.10.2,<2.0.0" --with "lxml>=4.9.0,<6.0.0" --with "pybliometrics>=4.4.1,<5.0.0" python academic_search_server.py
```

PubMed 闇€瑕佸湪鐜鍙橀噺 `PUBMED_EMAIL` 鎴?`mcp-server/config.toml` 涓厤缃偖绠便€係copus / ScienceDirect 鏄彲閫?provider锛屽鐢ㄦ湰鏈?`pybliometrics` 閰嶇疆锛岄粯璁よ鍙?`~/.config/pybliometrics.cfg`锛涗笉瑕佹妸 Elsevier API key 鍐欏叆鎻掍欢鏂囦欢銆俙search_papers` 鍙湁鍦?`sources` 鏄惧紡鍖呭惈 `scopus` / `sciencedirect` 鏃舵墠浼氳皟鐢?Elsevier-backed provider锛屼互閬垮厤鏃犳剰娑堣€?Elsevier API 閰嶉銆?

## MCP Tools

| Tool | 璇存槑 |
|------|------|
| `search_papers` | 榛樿涓夋簮骞跺彂鎼滅储锛涘彲鏄惧紡娣诲姞 Scopus / ScienceDirect |
| `get_paper_by_id` | 鎸?DOI/PMID/arXiv ID 鑾峰彇璇︽儏 |
| `get_citation` | 鏍煎紡鍖栧紩鐢ㄧ敓鎴?|
| `lookup_mesh` | MeSH 璇嶈〃鏌ヨ |
| `search_scopus` | Scopus 楂樼骇妫€绱?|
| `get_scopus_abstract` | Scopus 鎽樿/璇︽儏鍏冩暟鎹?|
| `get_scopus_citation_overview` | Scopus 寮曠敤姒傝 |
# REDACTED: sensitive-looking memory line
| `search_scopus_affiliations` / `get_scopus_affiliation` | 鏈烘瀯妫€绱笌璇︽儏 |
| `search_scopus_serial_titles` / `get_scopus_serial_title` | 鏈熷垔/杩炵画鍑虹増鐗╂绱笌璇︽儏 |
| `get_scopus_plumx_metrics` | PlumX 鎸囨爣 |
| `search_sciencedirect` | ScienceDirect 妫€绱?|
| `get_sciencedirect_article_metadata` | ScienceDirect 鏂囩珷鍏冩暟鎹?|
