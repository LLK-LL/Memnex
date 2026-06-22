---
name: serper-scrape
description: Search the web with Serper and scrape result pages into Markdown. Use when the user asks to 鎼滅储, 鏌ユ壘, 鏌ヨ祫鏂? 鎵捐祫鏂? 璋冪爺, search, look up, research, browse, scrape, 鎶撶綉椤? 鑾峰彇缃戦〉鍐呭, 缃戦〉杞?Markdown, URL 杞?Markdown, 鎻愬彇缃戦〉姝ｆ枃, or when researching GitHub repositories, README files, docs, API docs, project pages, release notes, blog posts, news, tutorials, or technical references from the web. Prefer this skill over generic web search when the user wants source material, page content, saved notes, or Markdown extraction.
---

# Serper Search & Scrape Skill

## Trigger Contract

Use this skill for:

- Web search where the user asks to collect, inspect, research, compare, summarize, or preserve source pages.
- GitHub/project research, including repository discovery, README extraction, release notes, issues, docs, API references, and tutorials.
- Any request that combines search/discovery with Markdown extraction or note saving.
- Any direct URL request where the expected output is page text, Markdown, cleaned article content, or an Obsidian-style note.

Do not use this skill for:

- Local files that are already downloaded; use `markitdown` when the task is file conversion.
- Browser UI testing, screenshots, clicking, login flows, or JavaScript-heavy interaction; use the Browser skill/tool.
- Pure factual questions where no source page needs to be preserved.

When uncertain between generic web search and this skill, choose this skill if the user says "鏌ヨ祫鏂?, "鎵捐祫鏂?, "璋冪爺", "GitHub", "鏂囨。", "璧勬枡鏁寸悊", "鎶撳彇", "杞?Markdown", or asks for source-backed notes.

# REDACTED: sensitive-looking memory line

> **瀹夊叏璀﹀憡**锛氭案杩滀笉瑕佸湪浠ｇ爜銆侀厤缃垨鍛戒护琛屽弬鏁颁腑纭紪鐮?API KEY銆傚缁堥€氳繃鐜鍙橀噺璇诲彇銆?

## 浣跨敤鏂瑰紡

浼樺厛浣跨敤 `scripts/` 鐩綍涓嬬殑杈呭姪鑴氭湰杩涜 API 璋冪敤锛岃€岄潪鐩存帴鍐?curl 鍛戒护锛?

### 鎼滅储
```bash
bash <skill_path>/scripts/serper-search.sh "<query>" [gl] [hl] [tbs] [num] [page]
```

### 鎶撳彇
```bash
bash <skill_path>/scripts/serper-scrape.sh "<url>" [includeMarkdown]
```

鍏朵腑 `<skill_path>` 鏄 skill 鐨勫畨瑁呯洰褰曘€傚涓嶇‘瀹氾紝鍙€氳繃 `which serper-scrape` 鎴栨煡璇?Claude skills 鐩綍瀹氫綅銆?

---

## API 鍙傝€?

### 鎼滅储 (Search)

**Endpoint**: `https://google.serper.dev/search` (POST)

| 鍙傛暟 | 绫诲瀷 | 蹇呴渶 | 璇存槑 |
|------|------|------|------|
| `q` | string | 鏄?| 鎼滅储鍏抽敭璇?|
| `gl` | string | 鍚?| 鍥藉浠ｇ爜锛岄粯璁?`us` |
| `hl` | string | 鍚?| 璇█浠ｇ爜锛岄粯璁?`en` |
| `tbs` | string | 鍚?| 鏃堕棿鑼冨洿绛涢€?|
| `num` | number | 鍚?| 杩斿洖缁撴灉鏁帮紝榛樿 10锛屾渶澶?100 |
| `page` | number | 鍚?| 椤电爜锛岄粯璁?1 |

**鏃堕棿鑼冨洿 (tbs)**: `qdr:h`(1灏忔椂) / `qdr:d`(24灏忔椂) / `qdr:w`(1鍛? / `qdr:m`(1涓湀) / `qdr:y`(1骞?

**鍝嶅簲鍏抽敭瀛楁**:
- `searchParameters` - 璇锋眰鍙傛暟鍥炴樉
- `knowledgeGraph` - 鐭ヨ瘑鍥捐氨锛堝瀛樺湪锛?
- `organic[]` - 鑷劧鎼滅储缁撴灉鍒楄〃锛坱itle, link, snippet, position锛?
- `peopleAlsoAsk[]` - 鐩稿叧闂瓟
- `relatedSearches[]` - 鐩稿叧鎼滅储

### 鎶撳彇 (Scrape)

**Endpoint**: `https://scrape.serper.dev` (POST)

| 鍙傛暟 | 绫诲瀷 | 蹇呴渶 | 璇存槑 |
|------|------|------|------|
| `url` | string | 鏄?| 鐩爣缃戦〉瀹屾暣 URL锛堥渶鍚?`https://`锛?|
| `includeMarkdown` | boolean | 鍚?| 杩斿洖 markdown 鏍煎紡锛岄粯璁?`true` |

**鍝嶅簲鍏抽敭瀛楁**: `markdown`(椤甸潰 markdown 鍐呭) / `text`(绾枃鏈? / `metadata`(鍏冩暟鎹?

---

## 缁勫悎宸ヤ綔娴?

**鎺ㄨ崘娴佺▼**锛氬厛鎼滅储鑾峰彇閾炬帴 鈫?绛涢€夋渶鐩稿叧鐨?鈫?鎶撳彇璇︽儏椤靛唴瀹广€?

```bash
# 姝ラ 1: 鎼滅储
bash scripts/serper-search.sh "Claude 4 Anthropic" "us" "en" "qdr:w" 5

# 姝ラ 2: 浠?organic[].link 鎻愬彇鎰熷叴瓒ｇ殑 URL

# 姝ラ 3: 鎶撳彇姣忎釜閾炬帴
bash scripts/serper-scrape.sh "https://example-article.com"
```

---

## 闄愬埗瑙勫垯锛堝繀椤婚伒瀹堬級

### 1. 鎶撳彇鏁伴噺闄愬埗

**姣忔鎼滅储鏈€澶氭姄鍙?5 涓綉椤?*銆傚鎼滅储缁撴灉瓒呰繃 5 鏉★紝鍙€夋嫨鏈€鐩稿叧鐨勫墠 5 涓€傝嫢鐢ㄦ埛鏄庣‘瑕佹眰鏇村锛岄渶鍛婄煡闄愬埗骞剁‘璁ゃ€?

### 2. 鍐呭淇濆瓨瑙勫垯

鎵€鏈夋姄鍙栫殑缃戦〉鍐呭蹇呴』澶勭悊鍚庝繚瀛樺埌 Obsidian锛?

| 鍐呭绫诲瀷 | 淇濆瓨鐩綍 |
|---------|---------|
| 鏅€氬唴瀹癸紙鏂伴椈銆佽鐐广€佹渚嬬瓑锛?| `~/tars/Resources/Web-Search/` |
| 鎶€鏈?宸ュ叿绫伙紙瀹樻柟鏂囨。銆丄PI銆丟itHub README銆佹暀绋嬬瓑锛?| `~/tars/Knowledge/` |

### 3. 鍐呭澶勭悊瑙勫垯

**蹇呴』淇濈暀**锛氭渚嬪拰绀轰緥銆佹牳蹇冭鐐广€佷簨瀹炲拰鏁版嵁銆侀噾鍙ョ簿鍗庛€佸紩鐢ㄩ摼鎺ャ€佸師鏂囬摼鎺?

**蹇呴』鍘婚櫎**锛氬鑸彍鍗?椤佃剼銆佸箍鍛娿€佸浘鐗囬摼鎺ワ紙鍏抽敭鍥捐〃闄ゅ锛夈€佽棰戝祵鍏ャ€佺ぞ浜ゆ寜閽€佽瘎璁哄尯锛堟湁浠峰€艰瘎璁洪櫎澶栵級銆佺浉鍏虫帹鑽愩€丆ookie 寮圭獥

### 4. 淇濆瓨鏂囦欢鏍煎紡

```markdown
---
title: {{椤甸潰鏍囬}}
source: {{鍘熷URL}}
date_scraped: {{鎶撳彇鏃ユ湡 YYYY-MM-DD}}
tags: [web-search, {{涓婚鏍囩}}]
---

# {{椤甸潰鏍囬}}

> 鏉ユ簮锛歔{{缃戠珯鍚嶇О}}]({{鍘熷URL}})

## 涓€鍙ヨ瘽鎬荤粨
{{鏍稿績瑕佺偣姒傛嫭}}

## 鍏抽敭鍐呭
{{澶勭悊鍚庣殑姝ｆ枃鍐呭}}

## 閲戝彞/瑕佺偣
- {{鎻愬彇鐨勯噾鍙ユ垨鍏抽敭瑙傜偣}}

## 寮曠敤閾炬帴
- [{{閾炬帴鏍囬}}]({{URL}})
```

---

## 娉ㄦ剰浜嬮」

# REDACTED: sensitive-looking memory line
- 鎼滅储鏃跺悎鐞嗕娇鐢?`tbs` 缂╁皬鏃堕棿鑼冨洿锛屾彁楂樼粨鏋滅浉鍏虫€?
- 鎶撳彇 URL 蹇呴』鏄畬鏁磋矾寰勶紙鍚?`https://`锛?
- 鏌愪簺缃戠珯鏈夊弽鐖帾鏂斤紝鎶撳彇澶辫触鏃跺憡鐭ョ敤鎴?
- 缁勫悎鎼滅储+鎶撳彇浼氭秷鑰楀娆?API 璋冪敤锛屾敞鎰忛厤棰?
