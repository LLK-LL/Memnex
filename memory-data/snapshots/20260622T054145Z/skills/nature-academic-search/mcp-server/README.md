# Unified Academic Search MCP Server

缁熶竴鐨勫鏈悳绱?MCP 鏈嶅姟鍣紝鏁村悎 CrossRef銆丳ubMed銆乤rXiv銆丼copus銆丼cienceDirect 鏁版嵁婧愩€?

## 宸ュ叿

| 宸ュ叿 | 鍔熻兘 |
|------|------|
| `search_papers` | 缁熶竴鎼滅储锛屾敮鎸佸鏁版嵁婧愬苟鍙?|
| `get_paper_by_id` | 鎸?DOI/PMID/arXiv ID 鑾峰彇璇︽儏 |
| `get_citation` | 鏍煎紡鍖栧紩鐢?(apa/nature/ieee 绛? |
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

## 閰嶇疆

鐜鍙橀噺:
- `PUBMED_EMAIL` - 蹇呭～锛孨CBI 瑕佹眰
# REDACTED: sensitive-looking memory line
- Elsevier / Scopus / ScienceDirect: 澶嶇敤 `pybliometrics` 閰嶇疆鏂囦欢锛岄粯璁や綅缃负 `~/.config/pybliometrics.cfg`

`search_papers` 榛樿妫€绱?CrossRef銆丳ubMed銆乤rXiv銆係copus / ScienceDirect 鏄彲閫?provider锛氬湪 `sources` 鏄惧紡浼犲叆 `scopus` / `sciencedirect`锛屾垨璋冪敤涓撶敤 Scopus / ScienceDirect 宸ュ叿鏃舵墠浼氳闂?Elsevier API銆傝繖鏍峰彲浠ラ伩鍏嶉粯璁ゆ悳绱㈡棤鎰忔秷鑰?Elsevier API 閰嶉锛涜嫢鏈満缂哄皯 `pybliometrics` 閰嶇疆锛屼細鍦ㄨ繑鍥?JSON 鐨?`errors` 瀛楁涓粰鍑哄搴旀暟鎹簮閿欒銆?

閰嶇疆鏂囦欢: `config.toml`

## 浣跨敤

鎻掍欢浼氶€氳繃 `uv run --no-project --directory <mcp-server> --with ... python academic_search_server.py`
鍚姩闅旂杩愯鐜銆傚伐鍏烽€氳繃 `academic-search` skill 璋冪敤銆?
