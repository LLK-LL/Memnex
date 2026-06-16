# ARS 鏁堣兘瑾槑

> **寤鸿妯″瀷锛欳laude Opus 4.7**锛屾惌閰?**Max plan**锛堟垨鍚岀瓑閰嶇疆锛夈€侽pus 4.7 鎺＄敤 adaptive thinking锛屼笉闇€瑕佹墜鍕曟寚瀹?thinking budget銆?
>
# REDACTED: sensitive-looking memory line
>
> 鍠崹浣跨敤鍊嬪垾 skill锛堝鍙敤 `deep-research` 鎴?`academic-paper-reviewer`锛夌殑娑堣€楁槑椤純灏戙€?

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line
|---|---|---|---|
| `deep-research` socratic | ~30K | ~15K | ~$0.60 |
| `deep-research` full | ~60K | ~30K | ~$1.20 |
| `deep-research` systematic-review | ~100K | ~50K | ~$2.00 |
| `academic-paper` plan | ~40K | ~20K | ~$0.80 |
| `academic-paper` full | ~80K | ~50K | ~$1.80 |
| `academic-paper-reviewer` full | ~50K | ~30K | ~$1.10 |
| `academic-paper-reviewer` quick | ~15K | ~8K | ~$0.30 |
| **瀹屾暣 pipeline锛?0 闅庢锛?* | **~200K+** | **~100K+** | **~$4-6** |
| + 璺ㄦā鍨嬮璀?| +~10K锛堝閮級| +~5K锛堝閮級| +~$0.60-1.10 |

*浠?~15,000 瀛楄珫鏂囥€亊60 绡囧紩鐢ㄧ偤鍩烘簴浼扮畻銆傚闅涙秷鑰楅毃璜栨枃闀峰害銆佷慨瑷傝吉鏁搞€佸皪瑭辨繁搴﹁€岀暟銆傝不鐢ㄤ互 Anthropic API 2026 骞?4 鏈堝畾鍍硅▓绠椼€?

## 寤鸿 Claude Code 瑷畾

| 瑷畾 | 鍔熻兘瑾槑 | 鍟熺敤鏂瑰紡 | 瀹樻柟鏂囦欢 |
|---|---|---|---|
# REDACTED: sensitive-looking memory line
| **Skip Permissions** | 璺抽亷姣忔宸ュ叿浣跨敤鐨勭⒑瑾嶆彁绀猴紝瀵︾従鍏?pipeline 涓嶄腑鏂风殑鑷富鍩疯 | 鍟熷嫊鏅傚姞涓?`claude --dangerously-skip-permissions` | [Permissions](https://docs.anthropic.com/en/docs/claude-code/cli-reference) 路 [Advanced Usage](https://docs.anthropic.com/en/docs/claude-code/advanced) |

> **鈿狅笍 Skip Permissions 娉ㄦ剰浜嬮爡**锛氭鏃楁鏈冨仠鐢ㄦ墍鏈夊伐鍏蜂娇鐢ㄧ殑纰鸿獚灏嶈┍妗嗐€傝珛鑷鏂熼厡浣跨敤 鈥?鍦ㄥ彲淇′换鐨勯暦鏅傞枔 pipeline 涓潪甯告柟渚匡紝浣嗘渻绉婚櫎鎵嬪嫊瀵╂牳鐨勫畨鍏ㄦ鍒躲€傚儏鍦ㄤ綘纰哄畾鎺ュ彈 Claude 鑷嫊鍩疯妾旀璁€瀵€乻hell 鎸囦护绛夋搷浣滄檪鎵嶅暉鐢ㄣ€?

### v3.7.0 Plugin agent 鑸囨ā鍨嬭矾鐢?

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

瀹屾暣 pipeline 瑷▓鐐?human-in-the-loop锛屾瘡鍊嬮殠娈甸兘闇€浣跨敤鑰呯⒑瑾嶃€傚鍕欎笂涓€娆″畬鏁村煼琛屾渻璺ㄨ秺鏁稿皬鏅傚埌鏁稿ぉ锛岄仩闀锋柤 Anthropic 鐨?prompt cache TTL锛? 鍒嗛悩锛夈€傚叐闋呯祼鏋滐細

1. **闅庢闁?cache miss 鏄父鎱嬨€?* 鐣?stage checkpoint 鍋滅暀瓒呴亷 5 鍒嗛悩锛屼笅涓€闅庢鏈冧互鏈揩鍙栫媭鎱嬭畝鍙?context銆傞€欐槸 human-paced pipeline 涓嶅彲閬垮厤鐨勬垚鏈€?
# REDACTED: sensitive-looking memory line

### v3.6.2 Sprint Contract 瀵╃鎴愭湰锛坄full` / `methodology-focus` 妯″紡蹇呰窇锛?

Schema 13 sprint contract 鎶婃瘡鍊?reviewer agent 鍒囨垚 Phase 1锛堜笉瑕嬭珫鏂囥€佸厛鎵胯瑭曞垎婧栧墖锛? Phase 2锛堢湅璜栨枃鍋氬绋匡級鍏╅殠娈点€傚凡 ship template 鐨勫叐鍊嬫ā寮忥紙`full` panel 5 + `methodology-focus` panel 2锛変笅锛屾瘡浣?reviewer 绱勭瓑鏂艰窇鍏╁€?LLM turn銆備繚鐣欐ā寮忥紙`re-review` / `calibration` / `guided` / `quick`锛夌董鎸?pre-v3.6.2 琛岀偤銆?

# REDACTED: sensitive-looking memory line
|---|---|---|
| `academic-paper-reviewer full` | 姣忎綅 reviewer 绱?+30-40% input + 灏忓箙 output 脳 5 浣?| Phase 1 璁€ contract template + 璜栨枃 metadata锛汸hase 2 璁€瀹屾暣璜栨枃 |
| `academic-paper-reviewer methodology-focus` | 鍚屼笂 shape锛宲anel 2 | EIC + methodology 鍏╀綅 reviewer 鍚勮窇鍏╅殠娈?|
| Synthesizer锛堝浐瀹氫竴鍊嬶級| +~2-3K input | 璁€ contract + 鍚?reviewer 杓稿嚭锛岃窇涓夋姗熸鍗旇 |

瀵︽脯寰呯湡瀵﹀ぇ瑕忔ā瀵╃寰屾牎婧栥€傚叐闅庢鏋舵鏄?gated mode 鐨勪笉鍙伕 overhead锛屼笉鏄?tunable銆?

### v3.4.0 compliance agent 鎴愭湰

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line
|---|---|---|---|
| `deep-research systematic-review`锛堝儏 2.5锛墊 +~5鈥?K | +~3鈥?K | +~$0.15 |
| 鍏?pipeline SR锛?.5 + 4.5锛墊 +~10鈥?5K | +~5鈥?K | +~$0.30 |
| `academic-paper full`锛坧re-finalize锛墊 +~3鈥?K | +~2鈥?K | +~$0.08 |

浠ヤ笂鐐烘棦鏈?per-skill 鎴愭湰涔嬩笂鐨勯澶栧閲忥紙鑸囦笂琛ㄥ叡鐢?15,000 瀛?/ 60 绡囧紩鐢ㄥ熀婧栵紝瑕嬩笂琛ㄤ笅鏂?footnote锛夈€傝法妯″瀷椹楄瓑鎴愭湰锛堣嫢鍟熺敤锛夌董鎸佷笉璁娿€?

### v3.6.3 Passport 閲嶇疆閭婄晫锛坥pt-in锛?

瑷畾 `ARS_PASSPORT_RESET=1` 寰岋紝姣忓€?FULL checkpoint 璁婃垚 context 閲嶇疆閭婄晫銆傞爯鏈熷伐浣滄祦绋嬶細

# REDACTED: sensitive-looking memory line
2. 寰?checkpoint 閫氱煡鎶勪笅 `[PASSPORT-RESET: hash=<hash>, stage=<completed>, next=<next>]` tag銆?
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

**浣曟檪閲嶇疆姣斿欢绾屽垝绠楋細**

# REDACTED: sensitive-looking memory line
- `systematic-review` 妯″紡锛宻tage 鐛ㄧ珛鎬х敱 Material Passport 绮剧⒑鐣屽畾銆?
- 鎾炲埌 5 鍒嗛悩 prompt cache TTL锛氶噸缃畵涓嬪€?stage 閲嶆柊璧风畻锛屼笉鐢ㄥ湪鑷冭叓 context 涓婁粯 cache miss銆?

**浣曟檪寤剁簩浠嶇劧姣旇純濂斤細**

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
- Flag OFF 鏅傦紝寤剁簩鏄笉璁婄殑 pre-v3.6.3 闋愯ō銆?

**Passport 妾旀浣嶇疆瑕忕磩锛?*

Orchestrator 闋愯ō鍦ㄧ洰鍓嶅伐浣滅洰閷勪笅灏嬫壘 `./passports/<slug>/` 鎴?`./material_passport*.yaml`銆傚皣 hash 瑙ｆ瀽鍒扮纰熶笂鐨?passport 妾旀鏄暣鍚堟柟鐨勮铂浠伙紝orchestrator 杓夊叆鍛煎彨绔伐鍏锋彁渚涚殑 passport銆傞爯瑷綅缃涓婃柟 `./passports/<slug>/` 瑕忕磩銆?

Resume 鎸囦护鍙畾缇?hash 鑸囧彲閬哥殑 stage/mode 瑕嗚搵锛?

```
resume_from_passport=<hash> [stage=<n>] [mode=<m>]
```

Resume 鎸囦护鏈韩娌掓湁璺緫瑾炴硶銆傚瑁?passport 浣嶇疆鍦ㄥ皥妗堢殑 `CLAUDE.md` 瑷畾锛屾垨鐢辨暣鍚堟柟鐨勫伐鍏峰湪鍛煎彨 orchestrator 鍓嶈檿鐞嗐€?

# REDACTED: sensitive-looking memory line

## 鏂囩嵒瑾炴枡搴皫鍏ワ紙v3.6.4+锛?

Material Passport 鐨?`literature_corpus[]` 娆勪綅鐢?*浣跨敤鑰呰嚜琛屾挵瀵殑 adapter** 鐢㈠嚭锛屼笉鏄?ARS 鏈韩銆倂3.6.4 闄勪笁鍊?reference adapter锛歚scripts/adapters/folder_scan.py`銆乣scripts/adapters/zotero.py`銆乣scripts/adapters/obsidian.py`銆傚煼琛屾柟寮忚垏鑷鎾板 adapter 鐨勬寚寮曡 [`scripts/adapters/README.md`](../scripts/adapters/README.md)銆?

### 鏁堣兘瀹氫綅

# REDACTED: sensitive-looking memory line
- Adapter 蹇呴爤鍏峰倷 determinism锛氬悓涓€浠?input 閲嶈窇鐢㈠嚭 byte-identical 杓稿嚭锛堟檪闁撴埑闄ゅ锛夈€?
- `literature_corpus[]` 渚?`citation_key` 鎺掑簭锛沗rejection_log.rejected[]` 渚?`source` 鎺掑簭銆?
- Adapter 杓稿嚭澶у皬鑸囪獮鏂欏韩澶у皬绶氭€ф垚闀枫€?00 绛?Zotero 鏇哥洰绱勭敘鍑?300 KB 鐨?passport YAML銆傚ぇ鍨嬭獮鏂欏韩寤鸿 ARS 娑堣不绔帯 lazy load銆?

### 灏庡叆灞ら倞鐣?

- 涓嶈畝 PDF 鍏у銆佷笉鍋氭枃瀛楁娊鍙栥€佷笉璺?OCR銆?
- 涓嶅懠鍙?Zotero Web API銆丯otion API 鎴栦换浣曢仩绔湇鍕欍€?
- 涓嶆姄浠樿不鐗嗗緦鍏у銆佷笉鐢ㄤ娇鐢ㄨ€呮啈璀夐€ｇ窔姗熸鍦栨浉椁ㄣ€?

閫欎簺閭婄晫鏄埢鎰忕殑锛屽弽鏄?ARS 鐨?data-layer 瀹氫綅锛欰RS 鏄?writing / review layer 鐨勬鏋讹紝瑾炴枡鏁村悎鐣欏湪 user-owned code銆傚闇€ API-based live-sync adapter锛岀敱浣跨敤鑰呬互涓夊€?reference adapter 鐐鸿捣榛炶嚜琛屾挵瀵€?

### 娑堣不绔暣鍚?

v3.6.5 璧凤紝Phase 1 鍏╁€嬫枃鐛?agent 閫忛亷 **corpus-first銆乻earch-fills-gap** 娴佺▼璁€鍙?`literature_corpus[]`锛歚deep-research/agents/bibliography_agent.md` 鑸?`academic-paper/agents/literature_strategist_agent.md`銆傚叐鑰呰蛋鐩稿悓鐨勪簲姝ユ祦绋嬭垏鍥涙 Iron Rule锛圫ame criteria / No silent skip / No corpus mutation / Graceful fallback on parse failure锛夈€係earch Strategy 鍫卞憡鏂板 PRE-SCREENED 鍙噸鐝惧崁濉婏紝鍒楀嚭宸茬磵鍏ワ紡鎺掗櫎锛忕暐閬庣殑 corpus entry锛屼甫鍚?F3 zero-hit 鑸?F4 provenance 鍫卞憡銆傛秷璨荤鍟熷嫊鎺?presence-based 鈥?passport 甯堕潪绌?`literature_corpus[]` 涓旇В鏋愭垚鍔熸檪鑷嫊閫插叆锛涜В鏋愬け鏁楁檪 fallback 鍒?external-DB-only flow锛屼甫 surface `[CORPUS PARSE FAILURE]`銆?

瀹屾暣 consumer 鍗斿畾瑕?[`academic-pipeline/references/literature_corpus_consumers.md`](../academic-pipeline/references/literature_corpus_consumers.md)銆俙citation_compliance_agent` 鐨?corpus 鏁村悎鐣欏埌 v3.6.6+銆?

### v3.6.5 corpus consumer 鎴愭湰锛坧resence 瑙哥櫦锛?

Material Passport 甯堕潪绌?`literature_corpus[]` 鏅傦紝Phase 1 璁€鍙栭噺闅?corpus 澶у皬绶氭€у闀枫€侾RE-SCREENED block 鐨?emit 鏈韩灞?prompt-layer锛堟垚鏈彲蹇界暐锛夛紱LLM 鎴愭湰渚嗚嚜 Step 1 pre-screening 鈥?灏嶆瘡绛?corpus entry 濂楃敤鐣跺墠 Inclusion / Exclusion 姊濅欢锛屾瘮灏?`title`锛堜竴瀹氭湁锛夎垏宸插～鐨勯伕濉瑒浣嶏紙`abstract` / `tags`锛夈€?

| Corpus 瑕忔ā | Step 1 pre-screening锛堟瘡浣?consumer锛墊 鍌欒ɑ |
|---|---|---|
| 绌?/ 涓嶅瓨鍦?| 0 | external-DB-only flow 缍寔鍘熸ǎ |
| ~50 绛嗭紙鍏稿瀷 Zotero 瀛愰泦锛墊 +~3-5K input + ~1-2K output | title + abstract 鎺冩弿 |
| ~200 绛?| +~10-15K input + ~3-5K output | title-only 鎺冩弿鐐轰富锛宎bstract 瑕栧～鍏呮儏娉?|
| ~500 绛嗭紙澶у瀷鏂囩嵒搴級| +~25-40K input + ~8-12K output | passport emit 鍓嶈€冩叜鍏堢簿绨?corpus |

Step 2 search-fills-gap 鍦?`uncovered_topics` 灏忥紙case A锛夋檪鏈冮檷浣?external-DB 鎴愭湰锛屽彲閮ㄥ垎鎶甸姺 Step 1銆傛法鏁堟噳瀵︽脯寰呯湡瀵?SR run instrumentation 寰屾牎婧栵紱鐩墠涓嶄笅绺介珨鏁稿瓧绲愯珫銆侾arse 澶辨晽绱勪竴鍊嬬煭 turn 鎴愭湰锛坧arse + emit `[CORPUS PARSE FAILURE]` + fallback锛夈€?
