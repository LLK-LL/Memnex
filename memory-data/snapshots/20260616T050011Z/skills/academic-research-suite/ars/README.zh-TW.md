# Academic Research Skills for Claude Code

> **Codex package note.** 閫欎唤妾旀鏄?vendored upstream ARS README锛屽収瀹逛粛鍦ㄨ鏄?
> Claude Code 鍘熺敓 plugin銆傚湪 `academic-research-skills-codex` 瑁★紝璜嬪畨瑁濅甫浣跨敤澶栧堡
> Codex skill锛涜 [`../../../README.md`](../../../README.md)銆?
> [`docs/SETUP.zh-TW.md`](docs/SETUP.zh-TW.md) 鑸?
> [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)銆俙/plugin install`銆佸師鐢?
> `/ars-*` slash command 瑷诲唺銆乸lugin hooks銆佽嚜鍕?Agent Team dispatch 绛?
> Claude-only 鍔熻兘锛屽湪 Codex 鐗堝彧鏈冭妯℃摤鎴栨槑纰哄垪鐐轰笉鏀彺銆?

[![Version](https://img.shields.io/badge/version-v3.9.4.1-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v3.9.4.1)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Sponsor](https://img.shields.io/badge/sponsor-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/crucify020v)

[English](README.md)

涓€濂楀畬鏁寸殑瀛歌鐮旂┒ Claude Code 鎶€鑳藉寘锛屾兜钃嬪緸鐮旂┒鍒拌珫鏂囧嚭鐗堢殑鍏ㄦ祦绋嬨€?

**30 绉掑畨瑁?*锛圕laude Code CLI / VS Code / JetBrains锛寁3.7.0+锛夛細

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

瑁濆畬璺?`/ars-plan`锛孉RS 鏈冪敤铇囨牸鎷夊簳灏嶈┍骞綘瑕忓妰绔犵瘈绲愭銆傞渶瑕佸墠缃浠舵垨鍌崇当 symlink 瀹夎璜嬬湅 [蹇€熷畨瑁漖(#蹇€熷畨瑁?銆?

> **AI 鏄綘鐨勫壇椐曢锛屼笉鏄闀枫€?* 閫欏伐鍏蜂笉鏈冨公浣犲璜栨枃銆傚畠铏曠悊鑻﹀伐 鈥?鎼滄枃鐛汇€佹帓鏍煎紡銆侀鏁告摎銆佹煡閭忚集涓€鑷存€?鈥?璁撲綘灏堟敞鍦ㄧ湡姝ｉ渶瑕佷綘鑵﹀瓙鐨勪簨锛氬畾缇╁晱椤屻€侀伕鏂规硶銆佽┊閲嬫暩鎿氱殑鎰忕京銆佸鍑恒€屾垜瑾嶇偤銆嶅緦闈㈤偅鍙ヨ┍銆?
>
> 璺?humanizer 涓嶅悓锛岄€欏伐鍏蜂笉鏄公浣犻毐钘忕敤 AI 鍗斾綔鐨勪簨瀵︼紝鑰屾槸骞綘鎶婇棞鏂囩珷鍝佽唱銆傞ⅷ鏍兼牎婧栧緸浣犻亷鍘荤殑鏂囩珷瀛哥繏浣犵殑鑱查煶锛屽浣滃搧璩鏌ユ姄鍑鸿畵鏂囧瓧璁€璧蜂締鍍忔鍣ㄧ敘鐨勬ā寮忋€傜洰妯欐槸鍝佽唱锛屼笉鏄伄鎺┿€?

### 鐐轰粈楹奸伕銆屼汉姗熷崝浣溿€嶈€屼笉鏄€屽叏鑷嫊銆嶏紵

Lu 绛変汉锛?026锛?Nature* 651:914-919锛夌櫦琛ㄧ殑 **The AI Scientist** 鏄涓€鍊嬬鍒扮鍏ㄨ嚜鍕曠殑 AI 鐮旂┒绯荤当锛屽叾鐢熸垚鐨勮珫鏂囬€氶亷 ICLR 2025 workshop 鐨勭洸瀵╋紙瑭曞垎 6.33/10锛寃orkshop 骞冲潎 4.87锛夈€備粬鍊戣嚜宸辩殑 Limitations 娈佃惤涔熷垪鍑轰簡閫欓绯荤当鏈冮亣鍒扮殑绲愭鎬уけ鏁楁ā寮忥細瀵︿綔閷銆佸够瑕哄椹楃祼鏋溿€佸彇宸х壒寰典緷璩淬€佸浣滈尟瑾よ鍖呰鎴愩€屾剰澶栫櫦鐝俱€嶃€佹柟娉曡珫鍋介€犮€佹鏋堕帠瀹氥€佸紩鐢ㄥ够瑕恒€?

ARS 寤虹珛鍦ㄩ€欏€嬪墠鎻愪笂锛?*浜洪鐮旂┒鑰?+ AI 鐨勭祫鍚堬紝姣旂磾鑷嫊鎴栫磾浜哄伐閮芥洿鑳介伩闁嬮€欎簺澶辨晽妯″紡**銆係tage 2.5 鑸?Stage 4.5 瑾犱俊闁橀杸鍩疯 7 椤為樆鏂峰紡妾㈡煡娓呭柈锛堣 [`academic-pipeline/references/ai_research_failure_modes.md`](academic-pipeline/references/ai_research_failure_modes.md)锛夛紝reviewer 涔熸彁渚?opt-in 鐨?calibration mode 鐢ㄤ娇鐢ㄨ€呰嚜鍌欑殑 gold set 娓噺 FNR/FPR銆?

[**Zhao 绛変汉**](https://arxiv.org/abs/2605.07723)锛?026-05锛夌洡榛炰簡 arXiv銆乥ioRxiv銆丼SRN銆丳MC 涓?250 钀瘒璜栨枃瑁＄殑 1.11 鍎勭瓎寮曠敤锛屼繚瀹堜及瑷?2025 骞村柈骞村氨鏈?146,932 绛嗗够瑕哄紩鐢紝涓﹁瀵熷埌 2024 骞翠腑鏄笂鍗囩殑鎷愰粸锛沚ioRxiv-to-PMC 閫欐閰嶅皪鐨勩€岄爯鍗版湰閫插埌姝ｅ紡鐧艰〃銆嶅够瑕哄瓨娲荤巼閬?85.3%銆備粬鍊戞妸銆岀湡瀵﹀紩鐢ㄨ鐢ㄤ締鏀拹琚紩鏂囩嵒鍏跺娌掓湁鎻愬嚭鐨勪富寮点€嶆弿杩扮偤鐣跺墠鏈В鐨勫晱椤屻€侫RS v3.7.1 鐐轰締婧?provenance 鍔犱笂 trust-chain frontmatter锛寁3.7.3 鐐烘湭渚嗙殑 claim-level 绋芥牳閶笂 locator 鍩虹寤鸿ō锛堜笁灞ゅ紩鐢?anchor锛夛紝涓﹀湪寮曠敤鏅傛甯跺嚭 advisory 棰ㄩ毆瑷婅櫉锛圓RS 鍏ч儴鎶婇€欐 claim-faithfulness 缂哄彛妯欒鐐恒€孡3銆嶏紝姝ょ偤 ARS 鐨勭敤瑭烇紝涓嶆槸璜栨枃鐨勭敤瑭烇級銆倂3.7.x 鐨勮ō瑷堝嫊姗熶締鑷?Zhao 绛変汉鐨?corpus-scale 鐧肩従锛汚RS 鏈韩鐨?corpus-scale 瑭曚及浠嶆槸鏈締宸ヤ綔銆?

v3.8 瑁滀笂 L3 缂哄彛鐨勫彟涓€鍗娿€倂3.7.3 璁撴瘡涓€绛嗗紩鐢ㄩ兘甯?locator anchor锛寁3.8 鍦ㄩ€欏€嬪熀绀庝笂鍔犱竴閬?opt-in 绋芥牳锛坄ARS_CLAIM_AUDIT=1`锛夛細鎶撳洖姣忎竴鍊?anchor 鎸囧悜鐨勫師濮嬫枃鏈紝鍒ゆ柗璜栨枃瑁＄殑 claim 鏄惁鐪熸湁琚┎寮曠敤鏀拹銆備簲椤炴柊鐨?HIGH-WARN annotation锛坈laim-not-supported銆乶egative-constraint-violation銆乫abricated-reference銆乤nchorless銆乧onstraint-violation-uncited锛夋渻鍦?formatter terminal hard gate 鐩存帴鏀斾笅杓稿嚭銆侰alibration 闅?release 鍑?20 绛?gold set锛屾帯 FNR<0.15銆丗PR<0.10 闆欓柧鍊硷紱姝ｅ紡鏀惧ぇ鎶曞叆鍓嶈鍏堟湁 calibration 璀夋摎锛坴3.8 spec 搂5锛夈€?

v3.3 鐨勯潏鎰熶締鑷?[**PaperOrchestra**](https://arxiv.org/abs/2604.05018)锛圫ong, Song, Pfister & Yoon, 2026, Google锛夛細Semantic Scholar API 椹楄瓑銆佸弽娲╂紡鍗旇銆乂LM 鍦栬〃椹楄瓑銆佸垎鏁歌粚璺¤拷韫ゃ€?

---

## 鏋舵鑸?pipeline

**馃憠 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** 鈥?瀹屾暣 pipeline 瑕栧湒锛氭祦绋嬪湒銆侀殠娈?脳 缍害鐭╅櫍銆佽硣鏂欏瓨鍙栨祦銆乻kill 渚濊炒鍦栥€佸搧璩枠闁€銆佹ā寮忔竻鍠€?

閫欎唤鏋舵鏂囦欢鍙栦唬浜嗗師鏈暎鍦?README 鍚勮檿鐨?pipeline 鎻忚堪銆傞棞鏂笺€屽摢鍊嬮殠娈佃窇浠€楹笺€嶇殑鎵€鏈夎硣瑷婇兘闆嗕腑鍦ㄤ竴鍊嬪湴鏂广€?

## 蹇€熷畨瑁?

**鍓嶇疆姊濅欢**

- [Claude Code](https://claude.ai/install.sh)锛堝缓璀版渶鏂扮増锛沺lugin packaging 闇€瑕佽繎鏈熺増鏈級
# REDACTED: sensitive-looking memory line
- *閬哥敤锛? Pandoc 鐢ㄦ柤 DOCX 杓稿嚭锛宼ectonic + 鎬濇簮瀹嬮珨 TC 鐢ㄦ柤 APA 7.0 PDF锛堢磾 Markdown 杓稿嚭鍏╁€嬮兘涓嶉渶瑕侊級

**Plugin 瀹夎锛坴3.7.0+锛屾帹钖︼級锛?*

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

**椹楄瓑鍙敤锛?* 璺?`/ars-plan` 涓︽弿杩颁綘姝ｅ湪瀵殑璜栨枃锛孉RS 鏈冪敤铇囨牸鎷夊簳灏嶈┍骞綘瑕忓妰绔犵瘈绲愭銆傛兂瑕佸柈娆℃脯瑭︾殑瑭辨敼璺?`/ars-lit-review "浣犵殑涓婚"`銆?

**馃憠 [docs/SETUP.zh-TW.md](docs/SETUP.zh-TW.md)** 鈥?瀹屾暣鎸囧崡锛氬畨瑁?Claude Code銆佽ō瀹?API key銆侀伕鐢ㄧ殑 Pandoc/tectonic锛圖OCX/PDF锛夈€佽法妯″瀷椹楄瓑锛坄ARS_CROSS_MODEL`锛夛紝浠ュ強浜旂ó瀹夎鏂瑰紡锛圥lugin銆佸皥妗?skills銆佸叏鍩?skills銆乧laude.ai Project銆乺epo clone锛夈€?

**鐢?Codex CLI锛?* 璜嬫敼瑁濆濡圭増锛歔`Imbad0202/academic-research-skills-codex`](https://github.com/Imbad0202/academic-research-skills-codex)銆傚悓涓€濂?workflow 鍏у锛孋odex 鍘熺敓鍖呰鐐哄柈涓€ `$academic-research-suite` skill锛屾彁渚?`ars-*` 鍒ュ悕銆?

## 鏁堣兘鑸囪不鐢?

# REDACTED: sensitive-looking memory line

## 浣跨敤鎸囧崡鑸囨枃绔?

- [瀛歌瀵綔涓嶈┎鏄竴鍊嬩汉鐨勪簨锛氫竴濂楅枊婧?AI 鍗斾綔宸ュ叿濡備綍鏀硅畩鐮旂┒鑰呯殑宸ヤ綔娴乚(https://open.substack.com/pub/edwardwu223235/p/ai?r=4dczl&utm_medium=ios) 鈥?瀹屾暣浣跨敤鎸囧崡锛堢箒楂斾腑鏂囷級
- [Academic Writing Shouldn't Be a Solo Act](https://open.substack.com/pub/edwardwu223235/p/academic-writing-shouldnt-be-a-solo?r=4dczl&utm_medium=ios) 鈥?Full pipeline walkthrough (English)

---

## 鍔熻兘鐗硅壊涓€瑕?

- **Deep Research** 鈥?13 鍊?Agent 鐨勭爺绌跺湗闅婏紝鏀彺铇囨牸鎷夊簳寮曞皫銆丳RISMA 绯荤当鎬у洖椤с€佹剰鍦栧伒娓€佸皪瑭卞仴搴峰害鐩ｆ帶銆佸彲閬歌法妯″瀷 DA銆丼emantic Scholar API 椹楄瓑銆?
- **Academic Paper** 鈥?12 鍊?Agent 鐨勮珫鏂囨挵瀵湗闅婏紝鍚ⅷ鏍兼牎婧栥€佸浣滃搧璩鏌ャ€丩aTeX 杓稿嚭寮峰寲銆佽瑕哄寲銆佷慨瑷傛暀绶淬€佸紩鐢ㄦ牸寮忚綁鎻涖€佸弽娲╂紡鍗旇銆乂LM 鍦栬〃椹楄瓑銆?
- **Academic Paper Reviewer** 鈥?7 鍊?Agent 鐨勫瑕栬鍚屽剷瀵╂煡锛?-100 鍝佽唱閲忚〃锛堜富绶?+ 3 浣嶅嫊鎱嬪鏌ヨ€?+ 榄旈浠ｈ█浜猴級锛屽惈璁撴闁€妾诲崝璀般€佹敾鎿婂挤搴︿繚鎸併€佸彲閬歌法妯″瀷 DA critique / calibration銆丷&R 杩芥函鐭╅櫍銆佸敮璁€绱勬潫銆?
- **Academic Pipeline** 鈥?10 闅庢鍏ㄦ祦绋嬭搴﹀櫒锛屽惈鑷仼鎳?checkpoint銆佸绋遍璀夈€佺礌鏉愯鐓с€佸彲閬?`repro_lock`銆佸彲閬歌法妯″瀷瑾犱俊椹楄瓑銆佷腑閫斿挤鍖栨鍒躲€佸垎鏁歌粚璺¤拷韫ゃ€?
- **璩囨枡瀛樺彇灞ょ礆妯欒ɑ**锛坴3.3.2+锛夆€?姣忓€?skill 瀹ｅ憡 `data_access_level`锛坄raw` / `redacted` / `verified_only`锛夛紝鐢?`scripts/check_data_access_level.py` 寮峰埗鍩疯銆傝ō瑷堥潏鎰熶締鑷?Anthropic 鐨?automated-w2s-researcher锛?026锛夈€傝┏瑕?[`shared/ground_truth_isolation_pattern.md`](shared/ground_truth_isolation_pattern.md)銆?
- **浠诲嫏椤炲瀷妯欒ɑ**锛坴3.3.2+锛夆€?姣忓€?skill 瀹ｅ憡 `task_type`锛坄open-ended` 鎴?`outcome-gradable`锛夈€傜洰鍓?ARS 鎵€鏈?skills 鐨嗙偤 `open-ended`銆?
- **Benchmark 鍫卞憡 Schema**锛坴3.3.5+锛夆€?JSON Schema + lint script锛岃姹傝獱瀵︾殑 benchmark 姣旇純鍫卞憡銆傝┏瑕?[`shared/benchmark_report_pattern.md`](shared/benchmark_report_pattern.md)銆?
- **Artifact 鍙噸鐝炬€?Lockfile**锛坴3.3.5+锛夆€?Material Passport 鏂板鍙伕 `repro_lock` 瀛愬崁濉娿€?*鏄ō瀹氭枃浠跺寲锛屼笉鏄噸鎾繚璀?* 鈥?LLM 杓稿嚭涓嶆槸浣嶅厓鍙噸鐝俱€傝┏瑕?[`shared/artifact_reproducibility_pattern.md`](shared/artifact_reproducibility_pattern.md)銆?

---

## 瀵﹂殯鐢㈠嚭灞曠ず

鏌ョ湅瀹屾暣 10 闅庢 pipeline 鐨勫闅涚敘鍑?鈥?鍖呭惈**鍚屽剷瀵╂煡鍫卞憡銆佽獱淇￠璀夊牨鍛娿€佸畬绋胯珫鏂?*锛?

**[鐎忚鎵€鏈?pipeline 鐢㈠嚭 鈫抅(examples/showcase/)**

| 鐢㈠嚭鐗?| 瑾槑 |
|---|---|
| [瀹岀璜栨枃锛堣嫳鏂囷級](examples/showcase/full_paper_apa7.pdf) | APA 7.0 鏍煎紡锛孡aTeX 绶ㄨ |
| [瀹岀璜栨枃锛堜腑鏂囷級](examples/showcase/full_paper_zh_apa7.pdf) | 涓枃鐗堬紝APA 7.0 |
| [瑾犱俊鍫卞憡 鈥?瀵╃鍓峕(examples/showcase/integrity_report_stage2.5.pdf) | Stage 2.5锛氭姄鍑?15 鍊嬭櫅妲嬪紩鐢?+ 3 鍊嬬当瑷堥尟瑾?|
| [瑾犱俊鍫卞憡 鈥?鏈€绲俔(examples/showcase/integrity_report_stage4.5.pdf) | Stage 4.5锛氱⒑瑾嶉浂鍥炴 |
| [鍚屽剷瀵╂煡绗竴杓猐(examples/showcase/stage3_review_report.pdf) | 涓荤法 + 3 瀵╂煡鑰?+ 榄旈浠ｈ█浜?|
| [瑜囧](examples/showcase/stage3prime_rereview_report.pdf) | 淇▊寰岄璀夊鏌?|
| [鍚屽剷瀵╂煡绗簩杓猐(examples/showcase/stage3_review_report_r2.pdf) | 杩借工瀵╂煡 |
| [鍥炶瀵╂煡鎰忚](examples/showcase/response_to_reviewers_r2.pdf) | 閫愰粸鍥炶 |
| [鍑虹増寰岀ń鏍稿牨鍛奭(examples/showcase/post_publication_audit_2026-03-09.pdf) | 鐛ㄧ珛鍏ㄥ紩鐢ㄧń鏍革細鐧肩従 21/68 绡囧晱椤岋紝閫氶亷浜?3 杓獱淇″鏌ヤ粛婕忕恫 |

---

## 鎼厤宸ュ叿锛欵xperiment Agent

濡傛灉浣犵殑鐮旂┒闇€瑕佸湪瀵綔鍓嶈窇瀵﹂锛堢▼寮忕⒓鎴栦汉宸ョ爺绌讹級锛孾Experiment Agent](https://github.com/Imbad0202/experiment-agent) 鎶€鑳藉～瑁?ARS Stage 1锛堢爺绌讹級鍜?Stage 2锛堝浣滐級涔嬮枔鐨勭┖缂恒€?

```
ARS Stage 1 鐮旂┒      鈫? RQ Brief + Methodology Blueprint
        鈫?
  experiment-agent     鈫? 鍩疯/绠＄悊瀵﹂ 鈫?椹楄瓑绲愭灉
        鈫?
ARS Stage 2 瀵綔      鈫? 鐢ㄩ璀夐亷鐨勫椹楃祼鏋滄挵瀵珫鏂?
```

**鍔熻兘**锛氬煼琛岀▼寮忕⒓瀵﹂锛圥ython銆丷 绛夛級涓﹀嵆鏅傜洠鎺с€佺鐞嗕汉宸ョ爺绌?protocol 鑸?IRB 鍊悊瀵╂煡銆?1 绋当瑷堣瑾ゅ伒娓€侀噸鐝炬€ч璀夈€?

# REDACTED: sensitive-looking memory line

---

## 浣跨敤鏂瑰紡

### 蹇€熼枊濮?

```
# 鍟熷嫊瀹屾暣鐮旂┒ pipeline
浣? "鎴戞兂鍋氫竴绡囬棞鏂?AI 灏嶉珮鏁欏搧淇濆奖闊跨殑鐮旂┒璜栨枃"

# 铇囨牸鎷夊簳寮曞皫妯″紡
浣? "寮曞皫鎴戠爺绌?AI 鍦ㄦ暀鑲茶閼戜腑鐨勬噳鐢?

# 寮曞皫寮忚珫鏂囨挵瀵?
浣? "寮曞皫鎴戝涓€绡囬棞鏂煎皯瀛愬寲褰遍熆鐨勮珫鏂?

# 瀵╂煡鐝炬湁璜栨枃
浣? "骞垜瀵╂煡閫欑瘒璜栨枃"锛堟帴钁楁彁渚涜珫鏂囷級

# 鏌ョ湅 pipeline 閫插害
浣? "閫插害" 鎴?"status"
```

### 鍊嬪垾 Skill 浣跨敤

#### Deep Research锛堟繁搴︾爺绌讹紝7 绋ā寮忥級

```
"鐮旂┒ AI 灏嶉珮绛夋暀鑲茬殑褰遍熆"                    鈫?full mode锛堝畬鏁寸爺绌讹級
"绲︽垜涓€浠?X 鐨勫揩閫熸憳瑕?                       鈫?quick mode锛堝揩閫熺啊鍫憋級
"骞垜鍋?X 鐨勭郴绲辨€ф枃鐛诲洖椤э紝鍚?PRISMA"        鈫?systematic-review mode
"寮曞皫鎴戠爺绌?X"                                鈫?socratic mode锛堣槆鏍兼媺搴曞紩灏庯級
"骞垜鏌ユ牳閫欎簺瑾硶"                            鈫?fact-check mode锛堜簨瀵︽煡鏍革級
"骞垜鍋氭枃鐛诲洖椤?                              鈫?lit-review mode锛堟枃鐛诲洖椤э級
"瀵╂煡閫欑瘒璜栨枃鐨勭爺绌跺搧璩?                      鈫?review mode锛堣珫鏂囧鏌ワ級
```

#### Academic Paper锛堝琛撹珫鏂囨挵瀵紝10 绋ā寮忥級

```
"骞垜瀵竴绡囪珫鏂?                              鈫?full mode锛堝畬鏁存挵瀵級
"寮曞皫鎴戝璜栨枃"                                鈫?plan mode锛堝紩灏庤鍔冿級
"鍏堝公鎴戞惌璜栨枃澶х侗"                            鈫?outline-only mode锛堝彧鍋氬ぇ缍憋級
"鎴戞湁鍒濈锛岄€欐槸瀵╃鎰忚"                      鈫?revision mode锛堜慨瑷傦級
"骞垜鏁寸悊閫欎簺瀵╃鎰忚鎴愪慨瑷傝矾绶氬湒"            鈫?revision-coach mode
"骞垜瀵€欑瘒鐨勬憳瑕?                            鈫?abstract-only mode锛堟憳瑕侊級
"鎶婇€欐壒璩囨枡瀵垚鏂囩嵒鍥為¨璜栨枃"                  鈫?lit-review mode锛堟枃鐛诲洖椤ц珫鏂囷級
"杞夋彌鎴?LaTeX" / "寮曠敤鏍煎紡杞?IEEE"            鈫?format-convert mode锛堟牸寮忚綁鎻涳級
"妾㈡煡寮曠敤鏍煎紡"                                鈫?citation-check mode锛堝紩鐢ㄦ鏌ワ級
"骞垜鐢熸垚 NeurIPS 鐨?AI 浣跨敤鎻湶"             鈫?disclosure mode锛圓I 鎻湶锛?
```

#### Academic Paper Reviewer锛堣珫鏂囧鏌ワ紝6 绋ā寮忥級

```
"瀵╂煡閫欑瘒璜栨枃"                                鈫?full mode锛堜富绶?+ R1/R2/R3 + 榄旈浠ｈ█浜猴級
"蹇€熻浼伴€欑瘒璜栨枃"                            鈫?quick mode锛堝揩閫熻浼帮級
"寮曞皫鎴戞敼閫查€欑瘒璜栨枃"                          鈫?guided mode锛堝紩灏庢敼閫诧級
"妾㈡煡鐮旂┒鏂规硶"                                鈫?methodology-focus mode锛堟柟娉曡珫鑱氱劍锛?
"椹楁敹淇▊"                                    鈫?re-review mode锛堝啀瀵╅鏀讹級
"鐢ㄦ垜鐨?gold set 鏍℃簴 reviewer"               鈫?calibration mode锛堟牎婧栵級
```

#### Academic Pipeline锛堝叏娴佺▼瑾垮害鍣級

```
"鎴戞兂鍋氫竴绡囧畬鏁寸殑鐮旂┒璜栨枃"                    鈫?寰?Stage 1 闁嬪瀹屾暣 pipeline
"鎴戝凡缍撴湁璜栨枃锛屽公鎴戝鏌?                      鈫?寰?Stage 2.5 閫插叆锛堝厛鍋氳獱淇″鏌ワ級
"鎴戞敹鍒板绋挎剰瑕嬩簡"                            鈫?寰?Stage 4 閫插叆
```

> Pipeline 绲愭潫鏅傝嚜鍕曠敘鍑?**Stage 6锛氶亷绋嬬磤閷?* 鈥?鍚珫鏂囧壍寤洪亷绋嬬磤閷勮垏 6 缍害鍗斾綔鍝佽唱瑭曚及锛?鈥?00 鍒嗭級銆?

### 鏀彺瑾炶█

- **绻侀珨涓枃** 鈥?浣跨敤鑰呬互涓枃灏嶈┍鏅傞爯瑷娇鐢?
- **English** 鈥?浣跨敤鑰呬互鑻辨枃灏嶈┍鏅傞爯瑷娇鐢?
- 瀛歌璜栨枃鑷嫊鐢㈠嚭闆欒獮鎽樿锛堜腑鏂?+ English锛?

> **浣跨敤鍏朵粬瑾炶█锛?* 铇囨牸鎷夊簳妯″紡锛坉eep-research锛夊拰 Plan 妯″紡锛坅cademic-paper锛夋帯鐢?*鎰忓湒鍖归厤**鍟熷嫊 鈥?鍋垫脯浣犵殑璜嬫眰鍚京锛岃€岄潪姣斿皪鐗瑰畾闂滈嵉瀛椼€傞€欎唬琛ㄥ畠鍊?*鏀彺浠讳綍瑾炶█**锛岀劇闇€椤嶅瑷畾銆?
>
> 涓嶉亷锛屼竴鑸殑 `Trigger Keywords` 鍗€濉婏紙姹哄畾 skill 鏄惁琚暉鍕曪級浠嶄互鑻辨枃鍜岀箒楂斾腑鏂囩偤涓汇€傚鏋滀綘鐧肩従 skill 鍦ㄤ綘鐨勮獮瑷€涓嬭Ц鐧间笉绌╁畾锛屽彲浠ュ湪鍚?`SKILL.md` 鐨?`### Trigger Keywords` 鍗€濉婁腑鍔犲叆浣犵殑瑾炶█鐨勯棞閸靛瓧锛屾彁楂樺尮閰嶄俊蹇冦€?

### 鏀彺寮曠敤鏍煎紡

- APA 7.0锛堥爯瑷紝鍚腑鏂囧紩鐢ㄨ鍓囷級
# REDACTED: sensitive-looking memory line
- MLA
- IEEE
- Vancouver

### 鏀彺璜栨枃绲愭

- IMRaD锛堝璀夌爺绌讹級
- 涓婚寮忔枃鐛诲洖椤?
- 鐞嗚珫鍒嗘瀽
- 鍊嬫鐮旂┒
- 鏀跨瓥绨″牨
- 鐮旇◣鏈冭珫鏂?

---

## Skill 瑭崇窗璩囪▕

鍚?agent 鐨勮伔璨垏鍚勯殠娈电敘鍑虹墿鐝惧凡绉昏嚦 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)銆傜増鏈櫉淇濈暀鍦ㄦ浠ョ董鎸?release metadata 闆嗕腑绠＄悊銆?

### Deep Research (v2.8)

13 鍊?Agent 鐨勭爺绌跺湗闅娿€傛ā寮忥細full銆乹uick銆乺eview銆乴it-review銆乫act-check銆乻ocratic銆乻ystematic-review銆傚畬鏁?agent 鍚嶅柈鑸囩敘鍑虹墿锛氳 ARCHITECTURE.md 搂3銆?

### Academic Paper (v3.0)

12 鍊?Agent 鐨勮珫鏂囨挵瀵?pipeline銆傛ā寮忥細full銆乸lan銆乷utline-only銆乺evision銆乺evision-coach銆乤bstract-only銆乴it-review銆乫ormat-convert銆乧itation-check銆乨isclosure銆傝几鍑猴細MD + DOCX锛圥andoc 鍙敤鏅傦級+ LaTeX锛圓PA 7.0 `apa7` class / IEEE / Chicago锛夆啋 tectonic 绶ㄨ PDF銆傚畬鏁?agent 鍚嶅柈鑸囧悇 phase 鑱疯铂锛氳 ARCHITECTURE.md 搂3銆?

### Academic Paper Reviewer (v1.8)

7 鍊?Agent 鐨勫瑕栬瀵╂煡锛屾惌閰?**0-100 鍝佽唱閲忚〃**銆傛ā寮忥細full銆乺e-review銆乹uick銆乵ethodology-focus銆乬uided銆乧alibration銆?*姹虹瓥灏嶇収锛?* 鈮?0 鎺ュ彈銆?5-79 灏忎慨銆?0-64 澶т慨銆?50 閫€绋裤€傜涓€杓鏌ュ湗闅?vs. 绮剧啊鍐嶅鍦橀殜鐨勫垎鐣岋細瑕?ARCHITECTURE.md 搂3 Stage 3 / Stage 3'銆?

### Academic Pipeline (v3.7)

10 闅庢瑾垮害鍣紝鍚獱淇￠璀夈€佸叐闅庢瀵╂煡銆佽槆鏍兼媺搴曟寚灏庛€佸崝浣滃搧璩浼般€侾ipeline 淇濊瓑锛氭瘡鍊嬮殠娈甸兘闇€浣跨敤鑰呯⒑瑾?checkpoint锛涜獱淇￠璀夛紙Stage 2.5 + 4.5锛変笉鍙烦閬庯紱R&R 杩芥函鐭╅櫍锛圫chema 11锛夌崹绔嬮璀変綔鑰呬慨瑷傚绋便€倂3.4 鏂板 Compliance Agent锛圥RISMA-trAIce + RAISE锛夋柤 Stage 2.5 / 4.5銆倂3.5 鏂板 **鍗斾綔娣卞害瑙€瀵熷摗**锛坄collaboration_depth_agent`锛屽儏璜鎬ц唱銆佹案涓嶉樆鎿嬫祦绋嬶級鏂兼瘡涓€娆?FULL/SLIM checkpoint 鑸?pipeline 瀹屾垚鏅傘€侻ANDATORY 瑾犱俊闁橀杸锛?.5 / 4.5锛夋槑纰鸿烦閬庤瀵熷摗锛岄伩鍏嶇█閲嬪悎瑕忔鏌ャ€傜悊璜栧熀绀庯細Wang & Zhang (2026), IJETHE 23:11銆傞€愰殠娈电煩闄ｏ紙agent銆佺敘鍑虹墿銆侀枠闁€锛夛細瑕?ARCHITECTURE.md 搂3銆?

---

## v3.0 鍎寲锛氭垜鍊戠櫦鐝句簡 AI 鐨勫摢浜涚祼妲嬫€ч檺鍒?

鍦ㄤ娇鐢?ARS 鎾板涓€绡囬棞鏂?AI 鑸囬珮鏁欑殑鍙嶆€濇枃绔犳檪锛屾垜鍊戦亣鍒颁簡涓夊€嬬祼妲嬫€у晱椤岋細

1. **妗嗘灦閹栧畾**锛欰I 鍦ㄧ郸瀹氭鏋跺収瓒婁締瓒婄簿绶伙紝浣嗙劇娉曡唱鐤戞鏋舵湰韬?
2. **璜傚獨鍌惧悜**锛氭瘡娆℃寫鎴伴瓟楝间唬瑷€浜虹殑鏀绘搳锛屽畠閮借畵姝ュ緱澶揩
3. **鎰忓湒鍋垫脯閷**锛氳槆鏍兼媺搴曟ā寮忓湪浣跨敤鑰呬粛鍦ㄦ帰绱㈡檪灏辨€ヨ憲鏀舵潫

### 鏀逛簡浠€楹?

- **榄旈浠ｈ█浜鸿畵姝ラ杸妾?*锛氬弽椐佸繀闋堣鍒?1-5锛屸墺4 鎵嶅厑瑷辫畵姝ャ€備笉鍏佽ū閫ｇ簩璁撴銆傛鏋堕帠瀹氬伒娓€?
- **铇囨牸鎷夊簳鎰忓湒鍋垫脯**锛氬伒娓娇鐢ㄨ€呮槸銆屾帰绱㈠瀷銆嶉倓鏄€岀洰妯欏瀷銆嶃€傛帰绱㈠瀷妯″紡鍋滅敤鑷嫊鏀舵潫銆?
- **灏嶈┍鍋ュ悍搴︽寚妯?*锛氭瘡 5 杓潨榛樿嚜妾紝鍋垫脯鎸佺簩鍚屾剰銆佽看閬胯绐併€侀亷鏃╂敹鏉熴€?
- **璺ㄦā鍨嬮璀?*锛氳ō瀹?`ARS_CROSS_MODEL` 鍟熺敤绗簩 AI 妯″瀷鐛ㄧ珛瀵╂煡銆傝┏瑕?[docs/SETUP.zh-TW.md](docs/SETUP.zh-TW.md)銆?
- **AI 鑷垜鍙嶆€濆牨鍛?*锛歅ipeline 绲愭潫寰岃嚜鍕曠敘鍑?AI 琛岀偤鑷銆?

閫欎簺鍎寲涓嶈兘瀹屽叏瑙ｆ焙 AI 鐨勭祼妲嬫€ч檺鍒垛€斺€斿畠鍊戣畵闄愬埗璁婂緱鍙銆佸彲杩借工銆佸彲琚汉椤炰粙鍏ャ€?

---

## 鎺堟瑠姊濇

鏈綔鍝佹帯鐢?[CC-BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 鎺堟瑠銆?

**浣犲彲浠ヨ嚜鐢憋細**
- 鍒嗕韩 鈥?瑜囪＝鍙婃暎甯冩湰浣滃搧
- 鏀逛綔 鈥?閲嶆贩銆佽綁鎻涖€佷互鏈綔鍝佺偤鍩虹閫茶鍓典綔

**鎯熼爤閬靛畧浠ヤ笅姊濅欢锛?*
- **濮撳悕妯欑ず** 鈥?浣犲繀闋堢郸浜堥仼鐣剁殑妯欑ず
- **闈炲晢妤€?* 鈥?浣犱笉寰楀皣鏈綔鍝佺敤鏂煎晢妤洰鐨?

**妯欑ず鏍煎紡锛?*
```
Based on Academic Research Skills by Cheng-I Wu
https://github.com/Imbad0202/academic-research-skills
```

---

## 璨㈢嵒鑰?

**鍚虫斂瀹?* (Cheng-I Wu) 鈥?浣滆€呰垏缍鑰?

**[aspi6246](https://github.com/aspi6246)** 鈥?璨㈢嵒鑰呫€倂3.1 鍎寲闈堟劅渚嗚嚜 [Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics)锛氬敮璁€绱勬潫妯″紡銆丄nti-Pattern 浣滅偤涓€绛夊叕姘戣ō瑷堛€佽獚鐭ユ鏋舵柟娉曪紙鏁欍€屽浣曟€濊€冦€嶈€岄潪鍙湁姝ラ锛夈€佺簿绨?skill 灏哄鍝插銆?

**[mchesbro1](https://github.com/mchesbro1)** 鈥?璨㈢嵒鑰呫€傛渶鍒濇彁鍑轰甫鎾板浜?IS Basket of 8 鏈熷垔娓呭柈锛圼Issue #5](https://github.com/Imbad0202/academic-research-skills/issues/5)锛夈€?

**[cloudenochcsis](https://github.com/cloudenochcsis)** 鈥?璨㈢嵒鑰呫€傚皣 IS 绔犵瘈寰?*Basket of 8* 鎿村厖鐐哄畬鏁寸殑 *Senior Scholars' Basket of 11*锛岃涓?*Decision Support Systems*銆?Information & Management*銆?Information and Organization*锛圼Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7)銆乕PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)锛夈€傝硣鏂欎締婧愶細[AIS Senior Scholars' List of Premier Journals](https://aisnet.org/page/SeniorScholarListofPremierJournals)銆?

---

## 鏇存柊绱€閷?

### v3.9.4.1锛?026-05-19锛夆€?v3.9.4 鏅傚簭椹楄瓑 post-ship hotfix锛?135 codex post-ship锛?

> Codex post-ship review 鎶撳埌 4 鍊?per-task subagent reviewer 婕忔帀鐨勭湡 bug銆侶otfix 涓€娆′慨榻婏細(1) `audit()` 鎶?`citation_provenance` 鎺ュ埌 P2 + P4锛岄亣鍒?ref slug 鍦?provenance.yaml 鏄?`confidence: low` 鎴?`conflict` 鏅傦紝椹楄瓑鍣ㄦ敼鐧?`TEMPORAL-METADATA-MISSING` 鑰屼笉鏄洿鎺ョ敤 timeline 鏃ユ湡鐣剁畻琛?ground truth锛坰pec 搂3.4 绗竴鎵?safety check 鍘熸湰娌掓帴绶氾級銆?2) `_date_to_interval` 瑁滈綂鍏ㄩ儴 schema-valid 鏃ユ湡褰㈢媭锛屽寘鎷?`YYYY-MM`锛圕rossref 鏈堢簿搴︼級鍜?`YYYY-MM-DD..YYYY-MM-DD`锛坕nterval锛夛紝v3.9.4 灏嶉€欏叐绋?silently `ValueError` 璺抽亷銆?3) P4 鍦?ref marker 缂哄腑鏅傚彲 bind 鐩存帴 prose 鏃ユ湡 鈥?銆孴he 2026 policy enabled the 2020 rollout銆嶉€欑ó鍙ョ従鍦ㄦ渻 trigger銆?4) `citation_provenance.schema.json` `confidence:high` allOf 鍔?`then.required`锛岃 absent-property bypass 婕忔礊銆?561 passed锛?12 鏂版脯瑭︺€? regression锛夈€侫RCHITECTURE.md 鍚屾瑁滈綂锛堝厛鍓嶅仠鍦?v3.8.0锛夈€?

### v3.9.4锛?026-05-18锛夆€?#135 鏅傚簭椹楄瓑灞わ紙advisory锛?

> Phase 4 鈫?5 閭婄晫鏂板姹哄畾鎬?advisory verifier锛屾兜钃?5 绋檪搴忓け鏁堟ā寮忥紙P1 鍥為¨绠楄銆丳2 鏅備唬閷疆寮曠敤銆丳3 姣旇純鍩烘簴鏈楂斿寲銆丳4 鍥犳灉鍊掔疆銆丳5 鐝惧湪寮忔寚绀鸿獮锛夈€傛柊 Phase 2 sibling `timeline_extraction_agent` 鎿佹湁 `phase2_investigation/timeline.yaml` + `phase2_investigation/citation_provenance.yaml`銆傞璀夎叧鏈?`scripts/temporal_integrity_audit.py` 鍩疯 5 閬撶⒑瀹氭€?pass銆侻3 鏅傚簭瀹屾暣鎬ч惖寰嬪姞鍏?`report_compiler_agent` + `draft_writer_agent`銆侻6-minimal锛欳rossref `issued` + pdftotext cover 绗竴鎵嬮璀夈€侻7-minimal锛氭棩鏈熷嚭铏?+ 姣旇純鍩烘簴瀵﹂珨鍖栥€侻5-stub锛氬儏浣跨敤鑰呭鍛婄殑 `version_family_id`銆俙literature_corpus_entry`銆乣claim_audit_result`銆乣claim_intent_manifest` 闆朵慨鏀广€俙bibliography_agent` 鏈敼鍕曪紙F2 涓嶈畩閲忥級銆? 鍊嬫柊 sidecar schema銆傝钃嬬巼浼拌▓锛?5-70% 鍩烘簴 / 鍚?M7 minimal 65-75%銆?549 passed锛?44 鏂版脯瑭︺€? regression锛夈€?

### v3.9.3锛?026-05-18锛夆€?#128 housekeeping锛坈lient utility 鎶藉嚭 + resolver dedup锛?

> 绱?refactor + 涓€鍊?latent bug fix锛屽緸 v3.9.0 `/simplify` review backlog 绲愭竻銆傛娊鍑?`scripts/_text_similarity.py`锛?-way client dedup锛歯ormalize / similarity / threshold / retry 甯告暩锛? `scripts/_passport_yaml.py`锛?-way migration tool dedup锛歳uamel.yaml round-trip config锛? 绉佹湁 `_resolve_by_doi_then_title` helper锛?-way resolver body dedup銆伮?.4 / 搂3.5 API surface 涓嶈畩锛夈€侽penAlex + Crossref 鐨?throttle 閲忔脯寰?`time.time`锛圢TP 涓嶅畨鍏級绲变竴鏀圭敤 `time.monotonic`锛岃垏 Semantic Scholar 灏嶉綂銆? 鍊?module-level cross-import 閮藉姞 dual-path try/except锛坰ibling-first銆乶amespace-package fallback锛変繚鎸?class identity锛涢澶栭爢鎵嬩慨浜?2 鍊?latent-broken 鐨?`import scripts.X` 璺緫銆?505 passed锛?23 鏂版脯瑭︺€? regression锛夈€?128 搂4锛圤A + CR 骞宠鍖栵級carry-over 鍒?#138銆?

### v3.9.2锛?026-05-18锛夆€?#133 phase boundary 鐔变慨

> #133 鏀跺熬锛坔ot-fix 灞わ級銆傞暦鏈熸灦妲嬩慨姝ｄ互 v3.10 active conductor 鍦?#134 杩借工銆傛柊澧烇細CLAUDE.md routing 閲愭竻闁橈紙璺?phase 绱犳潗 鈫?浠?a-d 閬搁爡閲愭竻锛屼笉闈滈粯 dispatch锛夈€?2 鍊?single-phase agent 鍔?prompt 纭?fence锛坄## Phase Boundary (v3.9.2)`锛夈€?6 鍊?multi-phase / phase-orthogonal / cross-phase-meta agent 鍒绘剰涓嶅姞 fence锛堣獱瀵?framing锛氱磾 prose placebo 鏈冮€犳垚鍋囨€?enforce 閷锛夈€乤dvisory verifier `scripts/check_pipeline_integrity.py` 浜嬪緦鍋垫脯 #133 pattern銆侭ehavioral smoke test 鍚?cross-model spot-check锛圤pus 4.7 100% / Sonnet + GPT-5.5 鈮?5%锛夈€?

### v3.9.1锛?026-05-18锛夆€?#129 + #130 client hardening

> v3.9.0 hot-fix銆傚寘 OpenAlex / Crossref response-read 澶辨晽鐐?`*Unavailable`锛?129锛夛紱`check_claim_audit_consistency` 灏嶉潪瀛椾覆 `manifest_id` 鍔?guard锛?130锛夈€傜劇 spec 璁婂嫊銆?

### v3.9.0锛?026-05-17锛夆€?#102 璺ㄧ储寮曚笁瑙掓脯閲?

> #102 鏀跺熬銆倂3.7.3 宸插畬鎴愬柈绱㈠紩锛圫emantic Scholar锛夋薄鏌撳伒娓紱v3.9.0 寤朵几鑷充笁绱㈠紩涓夎娓噺锛圫2 + OpenAlex + Crossref锛夛紝瀹氫綅鐐?*绱?advisory**銆俙contamination_signals` 鏂板鍏╁€?optional boolean锛坄openalex_unmatched`銆乣crossref_unmatched`锛夛紱manual-entry not-rule 灏嶇ū寤朵几銆侳inalizer 鍔犲叆 4-tier advisory matrix锛坘=0/1/2/3锛岃▓绠楃瘎鍦嶇偤鐝炬湁 `*_unmatched` 娆勪綅锛夛紝v3.7.3 鐨?legacy `CONTAMINATED-UNMATCHED`锛坘=1/k_max=1銆丼2-only case锛変繚鐣欍€侳ormatter pass-through allowlist 寰?3 姊濆欢浼歌嚦 9 姊濓紱refusal rules 1-10 渚?R-L3-2-E 涓嶈畩銆侾olicy layer锛坰trict modes銆乭ard-block tier銆乣venue_type` / `triangulation_policy`锛変緷 spec 搂2.3 寤惰嚦 v3.10銆俴=3 marker 鐐?`CONTAMINATED-TRIANGULATION-UNMATCHED`锛堟弿杩板彲瑙€娓従璞★紝涓嶆帹鏂锋垚鍥狅級銆傛柊澧?3 姊?firm rules锛歊-L3-2-C锛坘 瑷堢畻绡勫湇鐐虹従鏈夋瑒浣嶏級銆丷-L3-2-D锛堜笉寰?API 鎺ㄦ柗鍒嗛锛夈€丷-L3-2-E锛坮efusal list 涓嶆摯鍏咃紱pass-through allowlist 闋堣垏 finalizer 鍚屾寤朵几锛夈€?

**閬风Щ锛?* v3.7.3 corpus 鈥?璺?`python scripts/migrate_literature_corpus_to_v3_9_0.py PATH` 瑁滈綂鍏╁€嬫柊娆勪綅銆俻re-v3.7.3 corpus 鈥?**鍏?*璺?`migrate_literature_corpus_to_v3_7_3.py`锛屽啀璺?v3.9.0 閬风Щ宸ュ叿锛坰pec 搂3.7 daisy-chain锛泇3.9.0 宸ュ叿鍙嫊宸叉湁 `contamination_signals.semantic_scholar_unmatched` 鐨?entries锛夈€?

### v3.8.2锛?026-05-17锛夆€?#118 uncited audit_tool_failure 瑁滈潰

> #118 鏀跺熬銆俙ARS_CLAIM_AUDIT=1` 鐨?uncited 绱勬潫鍒ゆ柗璺緫鍘熸湰纰板埌 `JudgeInvocationError` 鏈冮潨榛樻浛鎻涙垚 `{"judgment": "NOT_VIOLATED"}`锛屾妸 HIGH-WARN 鐨?constraint check 鍦?transient judge 涓柗鏅傜洿鎺ュ悶鎺夈€倂3.8.2 鏀硅蛋鏂扮殑 `uncited_audit_failures[]` aggregate锛孧ED-WARN advisory tier 灏嶆噳 cited 璺緫 INV-14 row锛屼絾鐢ㄧ崹绔?schema 鍥犵偤 `claim_audit_result.ref_slug` 蹇呭～銆乽ncited 璺緫娌?ref 鍙秮銆?118 issue body 鍥涘€?option 鏈€寰岄伕浜?option 2锛堟柊 aggregate锛夛紱option 4锛坮e-raise 涓?abort 鏁存 audit锛夊洜鏈冨毚閲嶆姌鎼?audit coverage锛堢壒鍒ユ槸 judge endpoint 涓嶇┅鏅傦級琚惁姹恒€?

- **鏂?`uncited_audit_failure.schema.json` aggregate**锛坰pec 搂3.6锛夛細姣忕瓎 uncited sentence 脳 manifest pair 涓€鍊?entry锛岃閷?constraint judge raise `JudgeInvocationError` 鐨勬儏娉併€侳ault-class enum 鑸?cited 璺緫 INV-14 鐩稿悓锛坄judge_timeout` / `judge_api_error` / `judge_parse_error` / `cache_corruption` / `retrieval_api_error` / `retrieval_timeout` / `retrieval_network_error`锛夈€俙rule_version: D4-c-v1-uaf-v1`銆?
- **UAF-INV-1..UAF-INV-6 lint**锛坰pec 搂6 rule 4d锛夛細`finding_id` 鍞竴鎬с€乻coped_manifest_id 璺?aggregate integrity銆?M, C) pair integrity锛坢anifest_claim_id non-null 鏅傦級銆乸er-(sentence, manifest) dedup銆乺ationale fault_class 鍓嶇洞銆佽垏 `constraint_violations[]` cross-aggregate exclusivity銆?
- **Finalizer 搂5 MED-WARN advisory row**锛歛nnotation `[CLAIM-AUDIT-TOOL-FAILURE-UNCITED 鈥?<fault-class>]`锛実ate 閫氶亷锛坮etry-next-pass 鐐鸿鏁戞墜娈碉級銆侳ormatter REFUSE list 涓嶈畩 鈥?UAF 鏄?advisory銆?
- **Pipeline 鏁村悎**锛坄scripts/claim_audit_pipeline.py`锛夛細line 1211-1224 鐨?swallow site 绉婚櫎锛沗JudgeInvocationError` 鏀?emit UAF row + `continue` 鍒颁笅鍊?(sentence, manifest) pair銆俙constraint_violations[]` 涓嶆渻鍐嶈鍋?NOT_VIOLATED 姹℃煋銆?
- **Tests**锛氭柊澧?18 绛嗭紙15 绛?schema/lint TSUAFUncitedAuditFailureInvariants + 3 绛?pipeline integration TP23UncitedJudgeOutageEmitsUAF锛夈€侭aseline 694 鈫?712 tests銆? regression銆?
- **Agent doc**锛坄academic-pipeline/agents/claim_ref_alignment_audit_agent.md`锛夛細Output emission 琛ㄦ牸鏂板绗竷鍒楋紱Error handling 琛ㄦ牸寰?3 绋?surface 鎿存垚 4 绋紝鏂板 uncited 璺緫 UAF 鍒椼€?

### v3.8.0锛?026-05-16锛夆€?L3 Claim-Faithfulness Locator + Audit锛堥厤灏?milestone锛?

> v3.7.3 + v3.8 绔埌绔棞闁?L3锛坈laim-faithfulness锛夌己鍙ｃ€倂3.7.3 閶?locator 鍩虹寤鸿ō锛堟瘡绛嗗紩鐢ㄩ兘甯朵笁灞?anchor锛岀郸鏈締鐨勭ń鏍告姄寰楀埌鍘熸枃浣嶇疆锛夛紱v3.8 鍦ㄩ€欎箣涓婂姞涓€閬撶ń鏍?pass锛屽垽鏂峰紩鐢ㄤ締婧愭槸鍚︾湡鐨勬敮鎾愯珫鏂囩殑 claim锛岄仌鍙嶈€呭湪 formatter terminal hard gate 鐩存帴鏀斾笅銆傛湰娆?release 涔熷悎浣典簡寰?v3.7.0 寰岀疮绌嶇殑 5 鍊?audit-trail-shipped feature PR锛?104 / #105 / #108 / #111 / #115锛夈€?

- **#103 鈥?`claim_ref_alignment_audit_agent`**锛坴3.8 PR #121锛夛細opt-in锛坄ARS_CLAIM_AUDIT=1`锛岄爯瑷?OFF锛夌殑 Stage 4鈫? audit agent銆傚皪姣忕瓎鎶芥ǎ寮曠敤鍒ゆ柗鑸囧師鏂囨钀芥槸鍚︿竴鑷达紝emit `claim_audit_results[]` + `claim_intent_manifests[]` + `claim_drifts[]` + `uncited_assertions[]` + `constraint_violations[]` 浜斿€?aggregate銆侳inalizer 8 鍒?matrix 鎶?HIGH-WARN 椤炲垾锛圕LAIM-NOT-SUPPORTED / NEGATIVE-CONSTRAINT-VIOLATION / FABRICATED-REFERENCE / ANCHORLESS / CONSTRAINT-VIOLATION-UNCITED锛夊皫鍘?formatter REFUSE rules 6-10銆侰alibration runner 闅?release 鍑?20 绛?gold set锛圱-C1 FNR<0.15 + FPR<0.10銆乀-C2 per-class銆乀-C3 shape integrity锛夈€傚叡 8 杓?dual-track review锛圧1 codex + Gemini 3.1-pro-preview銆丷2-R8 鍦?Gemini quota 鐢ㄥ畬寰屾敼 codex-only锛夛紱trajectory R1 4P1+2P2 鈫?R8 0P1+4P2 ship gate銆?
- **v3.7.3 鈥?Three-Layer Citation Emission + contamination signals**锛圥R #98锛夛細`synthesis_agent` / `draft_writer_agent` / `report_compiler_agent` 鍔犱笂 `## Three-Layer Citation Emission (v3.7.3)` H2銆傛瘡鍊?`<!--ref:slug-->` 閮藉付 `<!--anchor:<kind>:<value>-->`锛宍<kind> 鈭?{quote, page, section, paragraph, none}`锛坬uote anchor 闄?25 瀛椾互鍏с€佸€奸渶 URL-encode锛夈€俙pipeline_orchestrator_agent` finalizer 鍗?5 cell 涓﹀姞 precedence-zero NO-LOCATOR 妾㈡煡銆俙formatter_agent` 鍦?hard gate 鍔犱笂灏?`[UNVERIFIED CITATION 鈥?NO QUOTE OR PAGE LOCATOR]` 鐨勬槑纰?refusal銆俙literature_corpus_entry.schema.json` 鏂板 optional 鐨?`contamination_signals: { preprint_post_llm_inflection, semantic_scholar_unmatched }` 鐗╀欢锛宍bibliography_agent` 鍦?ingest 鏅傝▓绠楀叐鍊嬭▕铏熴€?1 杓?review trajectory锛圕odex脳10 + Gemini cross-model脳1锛夋敹鏂?22 鍊?finding銆係pec锛歚docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md`銆傚閮ㄥ嫊姗燂細Zhao 绛変汉 arXiv:2605.07723锛?026-05锛夈€?
- **#108 鈥?AI disclosure policy-anchor renderer**锛?026-05-14锛夛細鍦ㄥ師鏈殑 venue-track renderer 涔嬪锛屾柊澧?PRISMA-trAIce / ICMJE / Nature / IEEE 鍥涙 policy-anchor disclosure 璺緫銆?
- **#111 鈥?`slr_lineage` emission on systematic-review 鈫?academic-paper handoff**锛?026-05-15锛夛細Schema 9 鏂板 optional 鐨?boolean `slr_lineage` 娆勪綅銆侾roducer 鏄?`pipeline_orchestrator_agent`锛堟瘡娆?handoff transition 瀵叆锛夛紝consumer 鏄?`disclosure` mode锛堣畝鍒板緦鎸?搂4.3 G2 invariant 璺敱鍒?`--policy-anchor=prisma-trAIce`锛夈€?
- **#104 鈥?README motivation锛歓hao 绛変汉 corpus-scale 璀夋摎閷ㄩ粸**锛?026-05-15锛夛細README + `README.zh-TW.md` 鍕曟娈典互 Zhao 绛変汉 146,932 绛嗗够瑕哄紩鐢ㄧ殑鐧肩従浣滅偤 v3.7.x 绶氳ō瑷堝嫊姗熺殑璀夋摎閷ㄩ粸銆?
- **#105 鈥?v3.7.3 contamination_signals 鍥炲～閬风Щ宸ュ叿**锛?026-05-15锛夛細`scripts/migrate_literature_corpus_to_v3_7_3.py` 灏?v3.7.3 鍓嶇殑 passport 鍙嶅悜瑷堢畻鍏╁€?contamination signals 涓﹁涓娿€?
# REDACTED: sensitive-looking memory line

### v3.7.0锛?026-05-05锛夆€?Claude Code Plugin 鎵撳寘

> Plugin 鎵撳寘鍗囩礆锛欰RS 鐝惧彲鍦?Claude Code CLI / VS Code / JetBrains 涓€琛岃锛坄/plugin marketplace add Imbad0202/academic-research-skills` + `/plugin install academic-research-skills`锛夈€傚師鏈殑 `git clone + symlink 鍒?~/.claude/skills/` 瀹夎娴佺▼涓嶈畩銆佺辜绾屾敮鎻达紱闆欒粚閮芥槸涓€绱氬叕姘戙€?

- **Plugin manifest 鑸?marketplace metadata**锛圥hase 1锛孭R #68锛夛細`.claude-plugin/plugin.json` 瀹ｅ憡鏁村€?suite锛? 鍊?skill 閫忛亷 `skills/` 鐩寗鐩稿皪 symlink 鑷嫊鎺㈢储锛夛紱`.claude-plugin/marketplace.json` 瑷诲唺 plugin锛屼娇鍠竴 GitHub-hosted endpoint 鍚屾檪鎻愪緵 marketplace listing 鑸?plugin 渚嗘簮銆俁EADME銆乣README.zh-TW.md`銆乣docs/SETUP.md` 閮藉姞鍏ラ洐杌屽畨瑁濇寚寮曘€?
- **10 鍊?slash command** 鍦?`commands/ars-*.md`锛圥hase 2.1锛孭R #69锛夊皣 `MODE_REGISTRY.md` 鐨勬鐩皪鏄犲埌 `/ars-<mode>` 瑙哥櫦銆傛瘡鍊?command frontmatter 閲樹綇妯″瀷璺敱锛歚opus` 绲?`full` 鑸?`revision-coach`锛堟灦妲嬭垏瀵╃瑙ｈ畝娣卞害锛夛紝`sonnet` 绲﹀叾浠?8 鍊嬨€備换浣曟儏澧冧笉鐢?Haiku銆?
- **3 鍊?plugin-shipped agent** 鍦?`agents/*_agent.md`锛圥hase 2.1锛孭R #69锛変互鐩稿皪 symlink 鎸囧悜 `deep-research/agents/` 鍏?v3.6.7 宸?hardened 鐨勪笅娓?agent锛歚synthesis_agent`銆乣research_architect_agent`銆乣report_compiler_agent`銆傚簳绶氭獢鍚嶄繚鐣欎互灏嶉綂 `scripts/check_v3_6_7_pattern_protection.py` hard-pin 璺緫鑸?INV-3 manifest-confined Clause 1 涓嶈畩寮忋€係ymlink锛堜笉瑜囪＝锛夌董鎸?single source of truth锛岄伩鍏?v3.6.7 搂6 inversion sweep + INV-1/2/3 lint 宸查棞闁夌殑 Pattern C3 鏀绘搳闈㈠啀闁嬨€?
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
- **`docs/PERFORMANCE.md` + `.zh-TW.md`** 鏂板銆寁3.7.0 Plugin agent 鑸囨ā鍨嬭矾鐢便€嶇瘈锛岃鏄?inherit 瑾炴剰鑸囩洰鍓?3-agent scope 閭婄晫銆?
- **璺ㄤ笁鍊?PR 鐨?codex review chain**锛? 杓?inline iterative review + 3 杓?fresh PR-level review锛屽叏閮ㄥ湪 merge 鍓嶆敹鏂傚埌 0 鍊?P0/P1/P2 finding銆侾hase 2.2 fresh PR review 鎶撳埌涓€鍊?P2锛坄${CLAUDE_PLUGIN_ROOT}` 娌?quote锛屽惈绌虹櫧鐨勫畨瑁濊矾寰戞渻 break锛夆€?inline 杓鎶撲笉鍒帮紝璀夊銆屽浣?review锛坕nline锛夈€嶈垏銆宑ontract review锛坒resh锛夈€嶅垎闆㈢殑鍍瑰€笺€?
- **娌掑嫊鐨勬澅瑗?*锛? 鍊?skill 鐩寗銆?5 鍊?mode銆乤gent prompt銆乻chema 妾旀銆乴int contract 鍏ㄤ笉璁娿€侾lugin 鎵撳寘鍙?*鏂板**闋傚堡浠嬮潰锛坄commands/`銆乣agents/`銆乣hooks/`銆乣.claude-plugin/`銆乣skills/` symlink dir銆? 鍊?source agent frontmatter 鍔?`model: inherit`锛夈€傛棦鏈?4.3k clone 瀹夎鐢ㄦ埗瀹屽叏涓嶇牬銆?

### v3.6.8锛?026-05-03锛夆€?Generator-Evaluator Contract Gate锛坴3.6.6 spec ship锛?

> 鍛藉悕瑾槑锛氭湰娆＄櫦琛屼氦浠?**v3.6.6 generator-evaluator contract** spec 鑸囧浣溿€?
> v3.6.6 鍥犲皥妗堟帓搴忔櫄鏂?v3.6.7 鎵嶈惤鍦帮紱design doc 鍏т粛淇濈暀 v3.6.6 鍏ч儴鍛藉悕浣滅偤
> contract gate 鐗堟湰锛宻uite release 妯?v3.6.8 缍寔 CHANGELOG 鍠閬炲銆?

- **Schema 13.1**锛坄shared/sprint_contract.schema.json`锛夊湪 Schema 13 涔嬩笂鍔犲叐鍊?`mode` enum 鍊硷紙`writer_full` + `evaluator_full`锛夈€佸叐鍊嬫柊 optional top-level 娆勪綅锛坄pre_commitment_artifacts` writer-only銆乣disagreement_handling` evaluator-only锛夈€?2 姊?`allOf` branch 寮峰埗 reviewer- / writer- / evaluator-conditional gate銆傛棦鏈?reviewer contract 鍦?Schema 13.1 涓?byte-equivalent validate锛埪?.6 zero-touch promise锛夈€?
- **鍏╁€嬫柊 shipped contract template**锛歚shared/contracts/writer/full.json`锛圖1鈥揇7銆丗1/F4/F2/F3/F0锛? `shared/contracts/evaluator/full.json`锛圖1鈥揇5銆丗1/F2/F3/F6/F4/F5/F0锛夈€係pec branch 涓婂師鏄?design-time artefact锛屾湰娆＄櫦琛?atomically promote 鐐?live shipped銆?
- **`academic-paper full` 妯″紡鍏у姞鍏?two-phase orchestration**锛歅hase 4 鎷嗘垚 Phase 4a锛坵riter paper-blind 闋愬厛鎵胯锛? Phase 4b锛坵riter paper-visible 鎾扮 + 鑷锛夛紱Phase 6 鎷嗘垚 Phase 6a锛坋valuator paper-blind 闋愬厛鎵胯锛? Phase 6b锛坋valuator paper-visible 瑭曞垎 + 姹虹瓥锛夈€俻hase-numbered `<phase4a_output>` / `<phase6a_output>` data delimiter 娌跨敤 v3.6.2 reviewer pattern銆侺int count summary锛歸riter 3+4 / evaluator 5+5 / reviewer 5+6锛坮eviewer 缍寔 zero-touch锛夈€?
# REDACTED: sensitive-looking memory line
- **Validator 鎿村厖**锛歚scripts/check_sprint_contract.py` 鍋?SC-* mode-gating audit锛圫C-5 + SC-11 reviewer-only锛汼C-9 璺ㄤ笁鍊?mode family 鍚勮畝灏嶆噳娆勪綅锛夈€倂alidator 鍠厓娓│寰?54 姊濆鍔犲埌 71 姊濓紙4 positive + 5 schema-branch negative + 2 搂3.6 reviewer regression + 6 mode-gating锛夈€?
- **Manifest CI lint**锛歚scripts/check_v3_6_6_ab_manifest.py` 寮峰埗 `tests/fixtures/v3.6.6-ab/manifest.yaml` 鐨?搂6.2 manifest schema + 搂6.5 git-tracked invariant銆俙.github/workflows/spec-consistency.yml` 鎶?sprint contract validation loop 鎿存垚鍚屾檪璺?reviewer + writer + evaluator 涓夊€?template directory锛屼甫鍔犲叆鏂扮殑 manifest CI lint 姝ラ銆?
- **A/B evidence fixture stub**锛坄tests/fixtures/v3.6.6-ab/`锛?0 鍊嬫獢妗堬級锛歮anifest + README + 6 paper-A inputs/baseline + 1 paper-C inputs/baseline + Stage 3 reviewer excerpt + 6 codex-judge baseline placeholder銆傜湡瀵?fixture data 鍦ㄥ緦绾?commit populate銆?

### v3.6.7锛?026-04-30锛夆€?涓嬫父 agent pattern protection锛圫tep 1+2锛?

- **涓夊€嬩笅娓?agent 鏀剁穵 13 / 18 鍊嬪凡鐭ュ够瑕鸿垏婕傜Щ pattern**锛歚synthesis_agent`锛圓1鈥揂5 鏁樹簨鍋达級銆乣research_architect_agent` survey-designer 妯″紡锛圔1鈥揃5 宸ュ叿鍋达級銆乣report_compiler_agent` abstract-only 妯″紡锛圕1鈥揅3 鍑虹増鍋达級銆備笁鍊?agent prompt 鍚勮嚜鍔犱笂 `PATTERN PROTECTION (v3.6.7)` 鍗€濉娿€?
- **`shared/references/` 澧炲姞鍥涗唤 reference 鏂囦欢**锛歚irb_terminology_glossary.md`銆乣psychometric_terminology_glossary.md`銆乣protected_hedging_phrases.md`銆乣word_count_conventions.md`銆俻rotection 姊濇寮曠敤閫欎簺妾旀璺緫鍋氱偤 operational contract銆?
- **璺ㄦā鍨?audit prompt 妯℃澘** 鍦?`shared/templates/codex_audit_multifile_template.md`锛屽惈涓冨€?audit dimension 鑸?`report_compiler_agent` bundle 蹇呰窇鐨勪笁娈靛紡 Section 4(f) 妾㈡煡銆備换涓€ sub-check 澶辨晽鍗?P1 finding銆?
- **闈滄厠 lint + 29 姊?mutation 娓│**锛歚scripts/check_v3_6_7_pattern_protection.py` 寮峰埗 protection 姊濇瀛樺湪鎬ц垏 obligation phrase 褰㈢媭锛沗scripts/test_check_v3_6_7_pattern_protection.py` 鎶?codex review 鐨?mutation 璀夋摎灏佸瓨鐐?unit test锛屾湭渚?lint 閫€鍖栨渻鍦?CI 娴笂渚嗐€傚叐鑰呴兘鎺ラ€?`.github/workflows/spec-consistency.yml`銆?
- **Codex review 绱€閷?*锛氫竷杓?`gpt-5.5` + `xhigh` 璺ㄦā鍨?review 鏀舵杺鍒?0 P1+P2 finding 鎵?SHIP銆係tep 6锛坥rchestrator runtime hook锛夎垏 Step 8锛堝悎鎴?eval case锛夎蛋 follow-up PR銆?

### v3.6.5锛?026-04-27锛夆€?Material Passport `literature_corpus[]` Consumer 鏁村悎

- **Phase 1 鍏╁€嬫枃鐛?consumer** 鎺ヤ笂锛歚deep-research/agents/bibliography_agent.md` 鑸?`academic-paper/agents/literature_strategist_agent.md`銆傜暥 passport 甯舵湁闈炵┖ `literature_corpus[]` 鏅傦紝鍏╄€呴兘璧扮浉鍚岀殑浜旀 **corpus-first銆乻earch-fills-gap** 娴佺▼锛屼甫閬靛畧鐩稿悓鐨勫洓姊?Iron Rule锛圫ame criteria / No silent skip / No corpus mutation / Graceful fallback on parse failure锛夈€?
- **PRE-SCREENED 鍙噸鐝惧崁濉?* 閫?Search Strategy 鍫卞憡锛氬垪鍑哄凡绱嶅叆锛忔帓闄わ紡鐣ラ亷鐨?corpus entry锛岄檮 F3 zero-hit 瑷昏В鑸?F4a鈥揊4f provenance 鍫卞憡锛堥嚌灏?`obtained_via` / `obtained_at` 閮ㄥ垎瀹ｅ憡鎯呭锛夈€俙final_included = pre_screened_included[] 鈭?external_included[]` 缍寔 neutral 鈥?bibliography entry 鑸?literature matrix row 涓嶆帥 provenance 妯欑堡銆?
- **Consumer 鍗斿畾鍙冭€冩枃浠?* 鍦?`academic-pipeline/references/literature_corpus_consumers.md`锛屽寘鍚?PRE-SCREENED 妯℃澘銆丅AD/GOOD 绡勪緥銆佸洓姊?Iron Rule 鑸?per-consumer 璁€鍙栨寚绀恒€?
- **CI lint** `scripts/check_corpus_consumer_protocol.py` 閫忛亷 manifest 椹呭嫊鐨?consumer 娓呭柈锛坄scripts/corpus_consumer_manifest.json`锛夊挤鍒朵節姊濆崝瀹氫笉璁婂紡銆?
- **Schema 9 caveat 閫€褰?*锛歚shared/handoff_schemas.md` 绉婚櫎 v3.6.4銆孋onsumer-side integration deferred to v3.6.5+銆嶄竴琛岋紝鏀规垚鎸囧悜 consumer 鍗斿畾鐨?backpointer銆?
- 鎺?presence-based 鍟熷嫊锛屼笉璁婃洿 schema銆佷笉寮曞叆鏂?env flag銆侾arse 澶辨晽 fallback 鍒?external-DB-only flow锛屼甫 surface `[CORPUS PARSE FAILURE]`銆俙citation_compliance_agent` 鐨?corpus 鏁村悎寤跺緦锛堢洰妯欑増鏈皣鏂?v3.8 寰屽啀瑷傦級銆?
- 鐒＄牬澹炴€ц畩鏇达紝鏃㈡湁浣跨敤鑰?adapter 涓嶉渶淇敼銆?

### v3.6.4锛?026-04-25锛夆€?Material Passport `literature_corpus[]` 杓稿叆鍩?

# REDACTED: sensitive-looking memory line
- **瑾炶█涓€х殑 adapter 濂戠磩** 鏀惧湪 `academic-pipeline/references/adapters/overview.md`锛氫换浣曡獮瑷€瀵殑绋嬪紡閮借兘璁€浣跨敤鑰呰嚜宸辩殑 corpus source 涓︾敘鍑虹鍚堝绱勭殑 `passport.yaml` + `rejection_log.yaml`銆侲ntry-level 閷 fail-soft銆乤dapter-level 閷 fail-loud銆佽几鍑洪爢搴忕⒑瀹氥€?
- **涓夊€?reference Python adapter** 鍦?`scripts/adapters/`锛歚folder_scan.py`锛堟獢妗堢郴绲辩殑 PDF 璩囨枡澶撅級銆乣zotero.py`锛圔etter BibTeX JSON export锛夈€乣obsidian.py`锛坴ault frontmatter锛夈€傚儏渚涜捣榛炲弮鑰冿紱闈?reference source 闋愭湡浣跨敤鑰呰嚜琛屽浣?adapter銆?
- **Rejection log 濂戠磩** 鍦?`shared/contracts/passport/rejection_log.schema.json`锛屾帯鐢ㄥ皝闁?enum 鐨?categorical reason 鍊硷紱姘搁仩杓稿嚭锛堢劇 rejection 鏅傜偤绌猴級銆?
- **CI 鎶婇棞**锛歚scripts/check_literature_corpus_schema.py` 椹?schemas + adapter examples锛沗scripts/sync_adapter_docs.py --check` 闃?schema鈫抎ocs drift锛涙柊 `pytest.yml` workflow 鍦?path-filtered 瑙哥櫦璺?`scripts/adapters/tests/`銆?
- **鍍呰几鍏ュ煚**锛歷3.6.4 鍙畾缇?schema 鑸?adapter 濂戠磩锛宑onsumer 鏁村悎鍒?v3.6.5 鎵嶆帴涓?`bibliography_agent` 鑸?`literature_strategist_agent`銆?
- 鐒＄牬澹炴€ц畩鏇淬€?

### v3.6.3锛?026-04-23锛夆€?閬哥敤寮?Passport 閲嶇疆閭婄晫

# REDACTED: sensitive-looking memory line
- Schema 9 鏂板 append-only `reset_boundary[]` ledger锛屽叐绋?entry kind锛坄kind: boundary` + `kind: resume`锛夈€侶ash 鐢?JSON Canonical Form + SHA-256锛屾惌閰?canonical placeholder 铏曠悊鑷垜鍙冪収鍟忛銆傞伕濉?`pending_decision` 璨犺铂 MANDATORY 鍒嗘敮姹虹瓥銆?
- 鏂?CI lint `scripts/check_passport_reset_contract.py`锛氫换浣曟彁鍒?flag 鐨勬獢妗堥兘蹇呴爤鎸囧悜娆婂▉鍗旇鏂囦欢銆?
- 鍗旇鏂囦欢锛歚academic-pipeline/references/passport_as_reset_boundary.md`銆?
# REDACTED: sensitive-looking memory line
- 鐒＄牬澹炴€ц畩鏇达紝flag 闋愯ō闂滈枆銆?

### v3.6.2锛?026-04-23锛夆€?瀵╃ Sprint Contract Hard Gate

v3.6.2 寮曞叆 Schema 13 sprint contract 鑸?hard-gate 绶ㄦ帓锛屽挤鍒跺绋夸汉鍦ㄩ柋璁€璜栨枃鍓嶅厛鎵胯瑭曞垎婧栧墖銆傛湰娆″彧鍕曞绋跨锛坮eviewer-only first test case锛夛紱writer/evaluator 鐣欏埌 v3.6.4銆傝┏瑕?CHANGELOG銆?

- **Schema 13 sprint contract**锛歚panel_size`銆乣acceptance_dimensions`銆乣failure_conditions`锛堝惈 `severity` 鍎厛搴?+ 闅?panel 璁婂嫊鐨?`cross_reviewer_quantifier`锛夈€乣measurement_procedure`銆侀伕鐢?`override_ladder`銆侀檺瀹?`agent_amendments`銆傞璀夊櫒锛歚scripts/check_sprint_contract.py`銆?
- **鍏╂ hard gate**锛氬绋夸汉鍏堝湪銆岃珫鏂囧収瀹圭洸銆峆hase 1 闋愬厛鎵胯瑭曞垎瑷堢暙锛孭hase 2 鎵嶇湅鍒拌珫鏂囷紱Phase 1 杓稿嚭鍖呭湪 `<phase1_output>...</phase1_output>` 璩囨枡鍒嗛殧绗﹀収锛岀府绐?self-injection 闈€?
- **鍚堟垚鑰呬笁姝ユ姊板崝璀?*锛氬缓妲嬭法瀵╃鐭╅櫍 鈫?渚?panel-relative quantifier + 瑾嶅彲琛ㄩ仈寮忚褰欒浼版瘡姊?`failure_condition` 鈫?鐢?`severity` 姹哄劒鍏堛€傜姝㈡搷浣滄竻鍠鍦?`editorial_synthesizer_agent`銆?
- **鍑鸿波鍏╀唤瀵╃妯℃澘**锛歚shared/contracts/reviewer/full.json`锛坧anel 5锛夎垏 `shared/contracts/reviewer/methodology_focus.json`锛坧anel 2锛夈€俙reviewer_re_review`銆乣reviewer_calibration`銆乣reviewer_guided` 涓夊€?mode 鍦?schema enum 涓繚鐣欙紝浣?v3.6.2 涓嶅嚭 template锛岀辜绾屾部鐢?pre-v3.6.2 琛岀偤锛沗reviewer_quick` 瀹屽叏鎺掗櫎鏂?enum 澶栥€?
- `academic-paper-reviewer` SKILL 鐗堟湰锛歚1.8.1 鈫?1.9.0`銆俙academic-pipeline` SKILL 鐗堟湰锛歚3.5.1 鈫?3.6.2`锛坰uite-version invariant锛夈€係uite 鐗堟湰鍗囪嚦 `3.6.2`銆?
- 瑭宠瑷▓绋?[`docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md`](docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md) 鑸囧崝瀹?[`academic-paper-reviewer/references/sprint_contract_protocol.md`](academic-paper-reviewer/references/sprint_contract_protocol.md)銆?

### v3.5.1锛?026-04-22锛夆€?閬哥敤寮?Socratic 瑾犲鎺㈡脯

v3.5.1 鏂板 Socratic Mentor 鐨勯伕鐢ㄥ紡瑾犲鎺㈡脯锛堣ō瀹?`ARS_SOCRATIC_READING_PROBE=1` 鍟熺敤锛夈€傞爯瑷棞闁夈€傝┏瑕?CHANGELOG銆?

# REDACTED: sensitive-looking memory line
- `deep-research` SKILL 鐗堟湰锛歚2.9.0 鈫?2.9.1`銆俙academic-pipeline` SKILL 鐗堟湰锛歚3.5.0 鈫?3.5.1`銆係uite 鐗堟湰鍗囪嚦 `3.5.1`銆?

### v3.5.0锛?026-04-21锛夆€?鍗斾綔娣卞害瑙€瀵熷摗锛圕ollaboration Depth Observer锛?

- **鏂板 agent**锛歚academic-pipeline` 鏂板 `collaboration_depth_agent`锛圓gent Team 寰?3 鎴愰暦鐐?4锛夈€傛瘡鍊?FULL/SLIM checkpoint 鑸?pipeline 瀹屾垚寰岋紙Stage 6 涔嬪緦锛夎Ц鐧硷紝渚?4 缍害 rubric 灏嶄娇鐢ㄨ€呰垏 AI 鐨勫崝浣滄ā寮忚鍒嗐€?*绱旇瀵熷缓璀帮紝姘镐笉闃绘搵娴佺▼**銆侻ANDATORY checkpoints锛圫tages 2.5 / 4.5 鐨勫畬鏁存€ф鏌ワ級**涓?*瑙哥櫦 observer锛屽畬鏁存€ч枠闁€瀹屽叏淇濈暀銆?
- **鏂板 rubric**锛歔`shared/collaboration_depth_rubric.md`](shared/collaboration_depth_rubric.md) v1.0銆傚洓鍊嬬董搴︼細Delegation Intensity銆丆ognitive Vigilance銆丆ognitive Reallocation銆乑one Classification锛圸one 1 / Zone 2 / Zone 3锛夈€傜悊璜栦緷鎿氱偤 Wang, S., & Zhang, H. (2026). "Pedagogical partnerships with generative AI in higher education: how dual cognitive pathways paradoxically enable transformative learning." *International Journal of Educational Technology in Higher Education*, 23:11. DOI [10.1186/s41239-026-00585-x](https://doi.org/10.1186/s41239-026-00585-x)銆?
- **Cross-model 鍒嗘椤紡妯欑ず锛屼笉榛橀粯骞冲潎**锛氱暥 `ARS_CROSS_MODEL` 瑷畾鏅傦紝observer 鏂煎叐鍊嬫ā鍨嬪悓鏅傚煼琛岋紱鑻ヤ换涓€缍害鍒嗗樊 > 2 鍒嗗嵆妯欒鐐?`cross_model_divergence`銆傚彟鎻愪緵 `ARS_CROSS_MODEL_SAMPLE_INTERVAL` 瑾挎帶鎴愭湰銆?
- **Short-stage guard**锛歴tage 鍏т娇鐢ㄨ€?turn < 5 鏅傛敞鍏ラ潨鎱?`insufficient_evidence` 鍗€濉婏紝涓嶆淳鐧煎叏妯″瀷 observer call銆?
- **鍙嶈珎濯氳绡?*锛氬垎鏁?鈮?7 蹇呴爤闄勫叿楂斿皪瑭?turn 寮曠敤锛沍one 3 瑙哥櫦 re-audit锛涚姝㈤紦鍕垫€ц獮瑷€銆?
- `academic-pipeline` SKILL 鐗堟湰锛歚3.3.0 鈫?3.4.0`銆係uite 鐗堟湰鍗囪嚦 `3.5.0`銆傛柊澧?lint `scripts/check_collaboration_depth_rubric.py` 鍔?10 鍊嬫脯瑭︺€?

### v3.4.0锛?026-04-20锛夆€?Compliance Agent + Schema 12

- **Compliance Agent锛坰hared锛?*锛氬柈涓€ mode-aware agent锛屽悓鏅傝窇 PRISMA-trAIce 17 闋咃紙闄?SR mode锛? RAISE 鍥涘師鍓?+ 8-role matrix銆傛帥杓夋棦鏈?Stage 2.5 / 4.5 Integrity Gate锛泃ier-based block锛圡andatory 鈫?block銆丠R 鈫?warn銆丷/O 鈫?info锛夈€傞潪 SR 鍏ュ彛鍙窇鍘熷墖銆亀arn-only銆?
- **Schema 12 compliance_report** 闄勫姞鍒?Material Passport 鐨?`compliance_history[]`锛坅ppend-only锛夈€?
- **涓夊洖鍚?user-override 闅庢**锛岃嚜鍕曟敞鍏?`disclosure_addendum` 鍒?manuscript銆傜劇娉曡閬挎彮闇层€?
- **Calibration 浠ラ€忔槑鍏竷鍙栦唬纭杸妾?*锛岃垏 `task_type: open-ended` 鑷唇銆?
- **Upstream freshness CI** 鍋垫脯 PRISMA-trAIce 涓婃父婕傜Щ锛坣on-blocking锛夈€?
# REDACTED: sensitive-looking memory line

### v3.3.6 (2026-04-15) 鈥?README 绮剧啊 + ARCHITECTURE 鏂囦欢

- 鏂板 `docs/ARCHITECTURE.md` 浣滅偤 pipeline 绲愭鐨勫柈涓€渚嗘簮锛堟祦绋嬨€佺煩闄ｃ€佽硣鏂欏瓨鍙栥€佷緷璩村湒銆佸搧璩枠闁€銆佹ā寮忥級銆傞€忛亷 PR #18 鍚堜降鍏?main銆?
- 鏂板 `docs/SETUP.md` / `docs/SETUP.zh-TW.md`锛堝墠缃渶姹傘€丄PI key銆丳andoc/tectonic銆佽法妯″瀷椹楄瓑銆佸洓绋畨瑁濇柟寮忥級锛屼互鍙?`docs/PERFORMANCE.md` / `docs/PERFORMANCE.zh-TW.md`锛坱oken 闋愮畻銆佸缓璀?Claude Code 瑷畾锛夈€俁EADME 浠ラ€ｇ祼鍙栦唬鍏у祵銆?
- 绮剧啊 README锛氱Щ闄?ASCII pipeline 鍦栬垏 16 闋?key-feature 娓呭柈锛堝凡琚?ARCHITECTURE.md 鍙栦唬锛夛紱Skill 瑭崇窗璩囪▕缍寔鐗堟湰铏熼尐榛烇紝璁€鑰呰烦鍒?ARCHITECTURE.md 搂3 鐪嬪悇 agent 鍚嶅柈銆?
- 瑷昏锛氭矑鏈変换浣?skill 鐨勫姛鑳借畩鍕曪紝绱旀枃浠堕噸妲嬨€俿uite version 鍗囩礆鑷?`3.3.6`銆?

### v3.3.5 (2026-04-15)
- 鏂板 `benchmark_report.schema.json` 鑸?Material Passport 鐨?`repro_lock` 鍙伕鍗€濉娿€傚叐鑰呴兘闄?pattern 鏂囦欢銆乴int銆佺瘎渚嬨€傞娆″紩鍏ユ寮忕殑 Python 闁嬬櫦渚濊炒娓呭柈锛坄requirements-dev.txt`锛夈€?

### v3.3.4 (2026-04-15) 鈥?README 鏇存柊绱€閷勫悓姝ヤ慨瑁?

- 鍚屾 `README.md` 鑸?`README.zh-TW.md` 鍏у祵鐨?changelog 鍗€濉婏紝瑁滀笂鍘熸湰缂烘紡鐨?`v3.3.3` 鑸?`v3.3.2` 鐧肩増鎽樿銆?
- 鎿村厖 `scripts/check_spec_consistency.py`锛屼箣寰?README changelog 鑻ュ啀婕傜Щ锛孋I 鏈冪洿鎺?fail銆?
### v3.3.3 (2026-04-15) 鈥?Release Prep + Lint 寮峰寲

- 寮峰寲 SKILL frontmatter lint锛氱己灏?closing `---` fence 鏅傦紝鐝惧湪鏈冩槑纰哄牨閷紝涓嶅啀鎶婃暣浠芥獢妗堝緦鍗婃瑾ょ暥鎴愬悎娉?YAML銆?
- frontmatter 鑻ュ彲琚?YAML 瑙ｆ瀽浣嗕笉鏄?mapping锛岀従鍦ㄦ渻鍥炲牨鍙畝閷锛岃€屼笉鏄洿鎺?crash銆?
- 淇涓嫳鏂?README 涓?post-publication audit showcase 閫ｇ祼澶辨晥鐨勫晱椤屻€?
- 鍦?spec consistency check 瑁滀笂 README 鐩稿皪閫ｇ祼椹楄瓑锛屼箣寰?dead link 鏈冪洿鎺ヨ畵 CI fail銆?
- 灏?DOCX 杓稿嚭濂戠磩鍦ㄦ枃浠朵腑绲变竴锛氱洿鎺ョ敘鍑?`.docx` 渚濊炒 Pandoc锛屽惁鍓囧洖閫€鐐?Markdown + 杞夋彌瑾槑銆?
- 瀹屾垚 `v3.3.3` 鐧肩増婧栧倷锛歴uite version bump锛宍academic-paper` -> v3.0.2锛宍academic-pipeline` -> v3.2.2銆?

### v3.3.2 (2026-04-15) 鈥?Data Access Level + Task Type Metadata

- 鎵€鏈夐爞灞?`SKILL.md` 鏂板 `metadata.data_access_level`锛屼甫浠?`raw`銆乣redacted`銆乣verified_only` 鐐哄挤鍒惰褰欍€?
- 鎵€鏈夐爞灞?`SKILL.md` 鏂板 `metadata.task_type`锛屼甫浠?`open-ended`銆乣outcome-gradable` 鐐哄挤鍒惰褰欍€?
- 鐐哄叐鍊?metadata 娆勪綅鏂板 lint script 鑸囧柈鍏冩脯瑭︼紝涓︽帴鍒?GitHub Actions spec consistency workflow銆?
- 鏂板 `shared/ground_truth_isolation_pattern.md`锛屼甫鍦?`shared/handoff_schemas.md` 涓涓婂皪鏂拌褰欑殑瑾槑鍏ュ彛銆?

### v3.3.1 (2026-04-14) 鈥?瑕忔牸涓€鑷存€т慨瑁?

- 鍚屾 README銆乣.claude/CLAUDE.md`銆乣MODE_REGISTRY.md` 鑸囧悇 `SKILL.md` 鐨?mode 鏁搁噺鑸囧叕闁嬬増鏈绀恒€?
- 淇璺ㄦā鍨嬫晿杩帮細鐩墠宸插浣滅殑鏄獱淇℃娊妯ｆ煡鏍歌垏鐛ㄧ珛 DA critique锛涘悓鍎曞鏌ョ鍏綅 reviewer 浠嶅湪瑕忓妰涓€?
- 閲愭竻 adaptive checkpoint 瑾炴剰锛歋LIM checkpoint 浠嶇劧蹇呴爤绛夊緟浣跨敤鑰呮槑纰虹⒑瑾嶃€?
- 鍐嶆鏄庣⒑鍖?Stage 2.5 鑸?Stage 4.5 瑾犱俊闂滃崱涓嶅彲璺抽亷銆?
- 鏂板杓曢噺 spec consistency 妾㈡煡鑸?GitHub Actions workflow锛岄伩鍏嶅緦绾屽啀鐧肩敓鏂囦欢婕傜Щ銆?

### v3.3 (2026-04-09) 鈥?PaperOrchestra 鍟熺櫦鐨勫挤鍖?

鏁村悎 [PaperOrchestra](https://arxiv.org/abs/2604.05018)锛圫ong, Song, Pfister & Yoon, 2026, Google锛夌殑鎶€琛撱€?

- **Semantic Scholar API 椹楄瓑** 鈥?Tier 0 绋嬪紡鍖栧紩鐢ㄥ瓨鍦ㄦ€ф煡鏍搞€侺evenshtein >= 0.70 妯欓姣斿皪銆丏OI 涓嶇鍋垫脯銆丼2 ID 鍘婚噸銆侫PI 涓嶅彲鐢ㄦ檪鍎泤闄嶇礆銆?
# REDACTED: sensitive-looking memory line
- **VLM 鍦栬〃椹楄瓑**锛堝彲閬革級鈥?鐢ㄨ瑕烘ā鍨嬮枆鐠版鏌ョ敓鎴愬湒琛ㄣ€?0 闋呮鏍告竻鍠紝鏈€澶?2 杓慨姝ｃ€?
- **鍒嗘暩杌岃贰鍗旇** 鈥?璺ㄤ慨瑷傝吉娆＄殑閫愮董搴﹁鍒嗗樊鐣拌拷韫わ紙7 鍊嬬董搴︼級銆傚伒娓€€姝ワ紙delta < -3锛夎Ц鐧煎挤鍒?checkpoint銆?
- **Stage 2 涓﹁鍖?* 鈥?瑕栬鍖栬垏璜栬瓑寤烘鍙湪澶х侗瀹屾垚寰屼甫琛屽煼琛屻€?
- 鏂扮増鏈細deep-research v2.8銆乤cademic-paper v3.0銆乤cademic-pipeline v3.2

### v3.2 (2026-04-09) 鈥?Lu 2026 Nature 鏁村悎

鏁村悎 Lu 绛変汉锛?026锛?Nature* 651:914-919锛夌殑鐮旂┒娲炶鈥斺€旂涓€鍊嬮€氶亷鐩插鐨勭鍒扮鍏ㄨ嚜鍕?AI 鐮旂┒绯荤当銆?

- **7 椤?AI 鐮旂┒澶辨晽妯″紡妾㈡煡娓呭柈** 鈥?鍦?Stage 2.5/4.5 闃绘柗绠＄窔锛氬伒娓浣滈尟瑾ゃ€佸够瑕哄椹楃祼鏋溿€佸彇宸х壒寰典緷璩淬€侀尟瑾ゅ寘瑁濈偤鐧肩従銆佹柟娉曞伣閫犮€佹鏋堕帠瀹氥€傛摯鍏呯従鏈?5 椤炲紩鐢ㄥ够瑕哄垎椤炪€?
- **Reviewer 鏍℃簴妯″紡**锛坅cademic-paper-reviewer v1.8锛夆€?opt-in 鐨?FNR/FPR/balanced accuracy 娓噺锛屼娇鐢ㄨ€呮彁渚?gold set銆? 娆￠泦鎴愩€佽法妯″瀷闋愯ō闁嬪暉銆乻ession 鍏у挤鍒堕檮鍔犱俊蹇冩彮闇层€?
- **鎻湶妯″紡**锛坅cademic-paper v2.9锛夆€?閲濆皪鐗瑰畾鏈熷垔/鏈冭鐨?AI 浣跨敤鑱叉槑鐢熸垚鍣ㄣ€倂1 娑佃搵 ICLR銆丯eurIPS銆丯ature銆丼cience銆丄CL銆丒MNLP銆?
# REDACTED: sensitive-looking memory line
- **蹇犲搴?鍘熷壍鎬фā寮忓厜璀?* 鈥?鎸?Lu 2026 Fig 1c 鍒嗛鎵€鏈?3 鍊?skill 鐨勬ā寮忋€?
- 鏂扮増鏈細academic-paper v2.9銆乤cademic-paper-reviewer v1.8銆乤cademic-pipeline v3.1

### v3.1.1 (2026-04-09) 鈥?璩囪▕绯荤当 Senior Scholars' Basket of 11

澶栭儴璨㈢嵒锛歔@mchesbro1](https://github.com/mchesbro1) 鏈€鍒濇彁鍑轰甫鎾板浜?IS Basket of 8 鏈熷垔娓呭柈锛圼Issue #5](https://github.com/Imbad0202/academic-research-skills/issues/5)锛夛紱[@cloudenochcsis](https://github.com/cloudenochcsis) 灏囧叾鎿村厖鐐哄畬鏁寸殑 Senior Scholars' Basket of 11锛圼Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7)銆乕PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)锛夈€傛洿鏂?`academic-paper-reviewer/references/top_journals_by_field.md` 绗?7 绡€锛岃涓?*Decision Support Systems*銆?Information & Management*銆?Information and Organization*銆傝硣鏂欎締婧愶細[AIS Senior Scholars' List of Premier Journals](https://aisnet.org/page/SeniorScholarListofPremierJournals)銆?

### v3.1 (2026-04-06) 鈥?鎶?Context Rot + 瑾嶇煡妗嗘灦 + 绮剧啊灏哄

闈堟劅渚嗚嚜 [aspi6246/Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics)銆?

**Wave 1锛氭姉 Context Rot 閷ㄥ畾**
- 4 鍊?skill 鍏?29 姊?Anti-Patterns锛堟瘡鍊?7-8 姊濓紝琛ㄦ牸鍚€岀偤浣曞け鏁椼€?銆屾纰鸿鐐恒€嶏級
- 22 鍊?IRON RULE 妯欒锛岀⒑淇濋暦灏嶈┍涓棞閸佃鍓囦笉琚伜蹇?
- 瀵╂煡鑰呭敮璁€绱勬潫锛坮eviewer 涓嶅彲淇敼璜栨枃鍘熺锛?

**Wave 2锛氳拷婧€?+ 瑾嶇煡妗嗘灦 + 涓€斿挤鍖?*
- R&R 杩芥函鐭╅櫍锛圫chema 11锛夛細Re-Review 鏂板銆屼綔鑰呰伈绋便€?銆屽凡椹楄瓑锛熴€嶆瑒浣嶏紝鐛ㄧ珛鏍稿淇▊瀹ｇū
- 3 鍊嬭獚鐭ユ鏋?reference 妾旀锛屾暀 agent銆屽浣曟€濊€冦€嶈€岄潪鍙槸銆屽仛浠€楹笺€嶏細
  - 璜栬瓑鑸囨帹鐞嗘鏋讹紙Toulmin 妯″瀷銆丅radford Hill 鍥犳灉鎺ㄧ悊銆佹渶浣宠В閲嬫帹璜栥€佽獚鐭ョ媭鎱嬪垎椤烇級
  - 瀵╂煡鍝佽唱鎬濈董妗嗘灦锛堜笁閺￠牠娉曘€佸父瑕嬪鏌ラ櫡闃便€佹牎婧栧晱椤岋級
  - 瀵綔鍒ゆ柗鍔涙鏋讹紙娓呮櫚搴︽脯瑭︺€佽畝鑰呮梾绋嬨€佸绉戣獮鎱嬨€佷慨瑷傛焙绛栫煩闄ｏ級
- 涓€斿挤鍖栨鍒讹細姣忔 stage 杞夋彌娉ㄥ叆灏嶆噳 IRON RULE + Anti-Pattern 鎻愰啋
- FULL checkpoint 鍓嶇殑 5 椤岃嚜鎴戞鏌ワ紙寮曠敤瀹屾暣鎬с€佽珎濯氳畵姝ャ€佸搧璩粚璺°€佺瘎鍦嶇磤寰嬨€佸畬鏁存€э級

**Wave 3锛氱簿绨?Skill 灏哄**
- SKILL.md 绺藉ぇ灏忓緸 142KB 闄嶈嚦 85KB锛?40%锛夛紝瑭崇窗鍗旇绉昏嚦 `references/` 鎸夐渶杓夊叆
- 鏂板 ~15 鍊?reference 妾旀锛坮e-review protocol銆乬uided mode銆乻ystematic review銆乸rocess summary 绛夛級
- 鎵€鏈?IRON RULE 淇濈暀鍦?SKILL.md锛涜┏绱板収瀹规寜闇€杓夊叆
- 鏂扮増鏈細deep-research v2.7銆乤cademic-paper v2.8銆乤cademic-paper-reviewer v1.7銆乤cademic-pipeline v3.0

### v3.0 (2026-04-03) 鈥?鍙嶈珎濯?+ 鎰忓湒鍋垫脯 + 璺ㄦā鍨嬮璀?+ AI 鑷垜鍙嶆€?
- **榄旈浠ｈ█浜鸿畵姝ラ杸妾?*锛坉eep-research + academic-paper-reviewer锛夛細鍙嶉蹇呴爤瑭曞垎 1-5銆傗墺4 鎵嶅厑瑷辫畵姝ャ€備笉鍏佽ū閫ｇ簩璁撴銆傝畵姝ョ巼杩借工銆傛鏋堕帠瀹氬伒娓€?
- **鏀绘搳寮峰害淇濇寔**锛坅cademic-paper-reviewer锛夛細DA 涓嶅洜琚弽椐佽€岃粺鍖栥€傚弽椐佽浼板崝璀板惈鍋忕Щ鍋垫脯銆?
- **鎰忓湒鍋垫脯灞?*锛坉eep-research socratic锛夛細鍋垫脯鎺㈢储鍨?vs. 鐩鍨嬨€傛帰绱㈡ā寮忓仠鐢ㄨ嚜鍕曟敹鏉燂紝鏈€澶ц吉鏁告彁鍗囪嚦 60銆傛瘡 5 杓噸鏂拌浼般€?
- **灏嶈┍鍋ュ悍搴︽寚妯?*锛坉eep-research socratic锛夛細姣?5 杓潨榛樿嚜妾紝鍋垫脯鎸佺簩鍚屾剰銆佽看閬胯绐併€侀亷鏃╂敹鏉熴€傚伒娓埌妯″紡鏅傝嚜鍕曟敞鍏ユ寫鎴版€у晱椤屻€?
- **璺ㄦā鍨嬮璀夊崝璀?*锛坰hared锛屽彲閬革級锛氱敤 GPT-5.4 Pro 鎴?Gemini 3.1 Pro 鍋氳獱淇￠璀?30% 鎶芥ǎ璺ㄦā鍨嬫鏌ヨ垏鐛ㄧ珛 DA critique銆傚悓鍎曞鏌ョ鍏綅 reviewer 浠嶅湪瑕忓妰涓紝灏氭湭瀵︿綔銆傝ō瀹?`ARS_CROSS_MODEL` 鐠板璁婃暩鍟熺敤鈥斺€旀湭瑷畾鏅傞浂闁嬮姺銆傚畬鏁磋ō瀹氭寚鍗楄 `shared/cross_model_verification.md`銆?
- **AI 鑷垜鍙嶆€濆牨鍛?*锛坅cademic-pipeline Stage 6锛夛細Pipeline 绲愭潫寰?AI 琛岀偤鑷鈥斺€擠A 璁撴鐜囥€佸仴搴疯鍫便€佽珎濯氶ⅷ闅绱氾紙LOW/MEDIUM/HIGH锛夈€佹鏋堕帠瀹氫簨浠躲€?
- 渚嗘簮锛氬洓杓警璀夊椹椾腑鐧肩従 DA 璁撴澶揩銆佽槆鏍兼媺搴曟ā寮忛亷鏃╂敹鏉熴€佹暣鍊嬭警璜栭帠瀹氬湪浜洪瑷畾鐨勬鏋朵腑銆?
- 鐗堟湰锛歞eep-research v2.5銆乤cademic-paper-reviewer v1.5銆乤cademic-pipeline v2.8

### v2.9.1 (2026-04-03) 鈥?Skill Metadata
- 鐐?4 鍊?SKILL.md 鍔犲叆 `status: active` 鍜?`related_skills` 浜ゅ弶寮曠敤
- 鏀彺 skill 鎺㈢储宸ュ叿鍙婅法鎶€鑳藉皫鑸?

### v2.9 (2026-03-27) 鈥?棰ㄦ牸鏍℃簴 + 瀵綔鍝佽唱妾㈡煡
- **棰ㄦ牸鏍℃簴**锛坅cademic-paper intake Step 10锛屽彲閬革級锛氭彁渚?3+ 绡囬亷鍘昏珫鏂囷紝pipeline 鏈冨缈掍綘鐨勫浣滈ⅷ鏍?鈥?鍙ュ瓙绡€濂忋€佽褰欏亸濂姐€佸紩鐢ㄦ暣鍚堟柟寮忋€傚浣滄檪浣滅偤杌熸€ф寚寮曪紱瀛哥瑕忕瘎姘搁仩鍎厛銆傚劒鍏堢礆绯荤当锛氬绉戣绡勶紙纭€э級> 鏈熷垔鎱ｄ緥锛堝挤锛? 鍊嬩汉棰ㄦ牸锛堣粺鎬э級銆傝 `shared/style_calibration_protocol.md`
- **瀵綔鍝佽唱妾㈡煡**锛坄academic-paper/references/writing_quality_check.md`锛夛細瀵綔鍝佽唱 checklist锛屾柤鍒濈鑷垜瀵╂煡鏅傚鐢ㄣ€? 澶ч锛欰I 楂橀牷瑭炲綑璀﹀憡锛?5 鍊嬭锛夈€佹榛炴ā寮忔帶鍒讹紙em dash 鈮?锛夈€侀枊闋虎瑭卞伒娓€佺祼妲嬫ā寮忚鍛婏紙涓夐爡鍒楄垑寮疯揩鐥囥€佸潎鍕绘钀姐€佸悓缇╄寰挵锛夈€佸彞瀛愰暦搴﹁畩鍖栨鏌ャ€傞€欐槸濂藉浣滆鍓?鈥?涓嶆槸閫冮伩鍋垫脯
- **Style Profile** 閫忛亷 academic-pipeline Material Passport 鏀滃付锛坄shared/handoff_schemas.md` Schema 10锛?
- **deep-research** report compiler 涔熷彲閬稿湴娑堣不閫欏叐鍊嬪姛鑳?
- 鐗堟湰锛歛cademic-paper v2.5銆乨eep-research v2.4銆乤cademic-pipeline v2.7

### v2.8 (2026-03-22) 鈥?SCR Loop Phase 1锛歋tate-Challenge-Reflect 鍙嶆€濇鍒?
- **Socratic Mentor Agent**锛坉eep-research + academic-paper锛夛細鏁村悎 SCR锛堣〃鎱?鎸戞埌-鍙嶆€濓級鍗旇
  - **Commitment Gate**锛氬湪姣忓€嬪堡绱?绔犵瘈杞夋彌鍓嶆敹闆嗕娇鐢ㄨ€呴爯娓紝鍐嶅憟鐝捐硣鏂?
  - **Certainty-Triggered Contradiction**锛氬伒娓珮淇″績瑾炲彞锛堛€岄’鐒躲€嶃€屾鐒＄枒鍟忋€嶏級锛岃嚜鍕曞紩鍏ュ弽闈㈣榛?
  - **Adaptive Intensity**锛氳拷韫?commitment 婧栫⒑鐜囷紝鍕曟厠瑾挎暣鎸戞埌闋荤巼
  - **Self-Calibration Signal (S5)**锛氭柊鏀舵杺瑷婅櫉锛岃拷韫や娇鐢ㄨ€呭湪灏嶈┍涓槸鍚﹀睍鐝捐嚜鎴戞牎婧栬兘鍔?
  - **SCR Switch**锛氫娇鐢ㄨ€呭彲闅ㄦ檪瑾€岃烦閬庨爯娓€嶉棞闁?SCR锛屾垨銆屾仮寰╅爯娓€嶉噸鏂伴枊鍟燂紝铇囨牸鎷夊簳寮忔彁鍟忎笉鍙楀奖闊?
- `deep-research/references/socratic_questioning_framework.md`锛氭柊澧?SCR Overlay Protocol锛屽皪鏄?SCR 涓夐殠娈靛埌铇囨牸鎷夊簳鍔熻兘
- 鏂板 `CHANGELOG.md`

### v2.7 (2026-03-09) 鈥?瑾犱俊椹楄瓑 v2.0锛氬弽骞昏鍏ㄩ潰鏀圭増
- **integrity_verification_agent v2.0**锛欰nti-Hallucination Mandate锛堢姝㈤潬 AI 瑷樻喍椹楄瓑锛夈€佹秷闄ょ伆鑹插湴甯跺垎椤烇紙鍍?VERIFIED/NOT_FOUND/MISMATCH锛夈€佸挤鍒?WebSearch audit trail銆丼tage 4.5 鐛ㄧ珛鍏ㄩ潰椹楄瓑銆丟ray-Zone Prevention Rule
- **宸茬煡寮曠敤骞昏 Pattern**锛? 椤炲垎椤炴硶锛圱F/PAC/IH/PH/SH锛屼締鑷?GPTZero 脳 NeurIPS 2025 鐮旂┒锛夈€? 绋鍚堟楱欐ā寮忋€佸鎴版渚嬨€佹枃鐛荤当瑷?
- **鍑虹増寰岀ń鏍?*锛氬皪鍏ㄩ儴 68 绡囧紩鐢ㄥ仛 WebSearch 閫愪竴椹楄瓑锛岀櫦鐝?21 绡囨湁鍟忛锛?1% 閷鐜囷級锛岃瓑鏄庡閮ㄦ煡璀夌殑蹇呰鎬?
- **璜栨枃淇**锛氱Щ闄?4 绡囨崗閫犲紩鐢ㄣ€佷慨姝?6 绡囦綔鑰呴尟瑾ゃ€佷慨姝?7 绡囨浉鐩窗绡€銆佷慨姝?2 绡囨牸寮忓晱椤?

### v2.6.2 (2026-03-09) 鈥?鎰忓湒鍖归厤妯″紡鍟熷嫊
- **deep-research**锛氳槆鏍兼媺搴曟ā寮忔敼鐐?*鎰忓湒鍖归厤**鍟熷嫊锛屽彇浠ｉ棞閸靛瓧姣斿皪銆傛敮鎻翠换浣曡獮瑷€ 鈥?鍋垫脯鍚京锛堝銆屼娇鐢ㄨ€呮兂瑕佸紩灏庡紡鎬濊€冦€嶏級鑰岄潪姣斿皪鐗瑰畾瀛椾覆銆?
- **academic-paper**锛歅lan 妯″紡鏀圭偤**鎰忓湒鍖归厤**鍟熷嫊銆傚伒娓剰鍦栦俊铏熷銆屼娇鐢ㄨ€呬笉纰哄畾濡備綍闁嬪銆嶃€屼娇鐢ㄨ€呮兂瑕侀€愭寮曞皫銆嶏紝涓嶉檺瑾炶█銆?
- 鍏╁€嬫ā寮忔柊澧?*闋愯ō瑕忓墖**锛氱暥鎰忓湒妯＄硦鏅傦紝鍋忓ソ `socratic`/`plan` 鑰岄潪 `full` 鈥?鍏堝紩灏庢瘮杓冨畨鍏ㄣ€?
- 闆欏堡鏋舵锛歀ayer 1锛坰kill 鍟熷嫊锛夌敤闆欒獮闂滈嵉瀛楁彁楂樺尮閰嶄俊蹇冿紱Layer 2锛坢ode 璺敱锛夌敤瑾炶█鐒￠棞鐨勬剰鍦栦俊铏熴€?

### v2.6.1 (2026-03-09) 鈥?闆欒獮瑙哥櫦闂滈嵉瀛?
- **deep-research**锛氭柊澧炵箒楂斾腑鏂囪Ц鐧奸棞閸靛瓧锛屾兜钃嬩竴鑸暉鍕曞拰铇囨牸鎷夊簳妯″紡銆?
- **academic-paper**锛氭柊澧炵箒楂斾腑鏂囪Ц鐧奸棞閸靛瓧鍙?Plan Mode 瑙哥櫦鍗€濉娿€?
- 鍏╀唤 mode selection guide 鍔犲叆闆欒獮绡勪緥鍙婁腑鏂囧皥灞閬告儏澧冦€?

### v2.6 / v2.4 / v1.4 (2026-03-08) 鈥?15+ 闋呮敼閫?
- **deep-research v2.3**锛氭柊澧炵郴绲辨€ф枃鐛诲洖椤?/ PRISMA 妯″紡锛堢 7 妯″紡锛夛紱3 鍊嬫柊 agent锛坮isk_of_bias銆乵eta_analysis銆乵onitoring锛夛紱PRISMA 鍗旇/鍫卞憡妯℃澘锛涜槆鏍兼媺搴曟敹鏂傛簴鍓囷紙4 瑷婅櫉 + 鑷嫊绲愭潫锛夛紱蹇€熸ā寮忛伕鎿囨寚鍗?
- **academic-paper v2.4**锛? 鍊嬫柊 agent锛坴isualization銆乺evision_coach锛夛紱淇▊杩借工妯℃澘鍚?4 绋媭鎱嬶紱寮曠敤鏍煎紡杞夋彌锛圓PA鈫擟hicago鈫擬LA鈫擨EEE鈫擵ancouver锛夛紱绲辫▓瑕栬鍖栨婧栵紱铇囨牸鎷夊簳鏀舵杺婧栧墖锛涗慨瑷傚京鍘熺瘎渚嬶紱**LaTeX 杓稿嚭寮峰寲** 鈥?寮峰埗 `apa7` document class銆乣ragged2e` + `etoolbox` 鏂囧瓧灏嶉綂淇銆佽〃鏍兼瑒瀵叕寮忋€侀洐瑾炴憳瑕佺疆涓€佹婧栧瓧楂旈泦锛圱imes New Roman + 鎬濇簮瀹嬮珨 VF + Courier New锛夈€佸儏 tectonic 绶ㄨ PDF
- **academic-paper-reviewer v1.4**锛?-100 鍝佽唱閲忚〃鍚鐐烘寚妯欙紱姹虹瓥灏嶇収锛堚墺80 鎺ュ彈銆?5-79 灏忎慨銆?0-64 澶т慨銆?50 閫€绋匡級锛涘揩閫熸ā寮忛伕鎿囨寚鍗?
- **academic-pipeline v2.6**锛氳嚜閬╂噳 checkpoint锛團ULL/SLIM/MANDATORY锛夛紱Phase E 瀹ｇū椹楄瓑锛涚礌鏉愯鐓э紙Material Passport锛夋敮鎻翠腑閫旈€插叆锛涜法 skill 妯″紡椤у晱锛?4 鎯呭锛夛紱鍦橀殜鍗斾綔鍗旇锛涘挤鍖栭姕鎺?schema锛? 鍊嬪惈椹楄瓑瑕忓墖锛夛紱瑾犱俊瀵╂煡澶辨晽寰╁師绡勪緥

### v2.4 / v1.3 (2026-03-08)
- **academic-pipeline v2.4**锛氭柊澧?Stage 6 閬庣▼绱€閷?鈥?鑷嫊鐢熸垚绲愭鍖栬珫鏂囧壍寤洪亷绋嬬磤閷勶紙MD 鈫?LaTeX 鈫?PDF锛屼腑鑻遍洐瑾烇級锛涘繀鍚渶寰屼竴绔狅細**鍗斾綔鍝佽唱瑭曚及**锛? 鍊嬬董搴﹀悇瑷?1鈥?00 鍒嗭紙鏂瑰悜瑷畾銆佹櫤璀樿并鐛汇€佸搧璩妸闂溿€佽凯浠ｇ磤寰嬨€佸娲炬晥鐜囥€佸緦瑷缈掞級锛屽惈瑾犲鍥為鑸囨敼閫插缓璀帮紱pipeline 寰?9 闅庢鎿村睍鐐?10 闅庢

### v2.3 / v1.3 (2026-03-08)
- **academic-pipeline v2.3**锛歋tage 5 瀹氱闅庢鐝惧湪鏈冨厛瑭㈠晱鏍煎紡棰ㄦ牸锛圓PA 7.0 / Chicago / IEEE锛夛紱PDF 蹇呴爤寰?LaTeX 缍?`tectonic` 绶ㄨ锛堢姝?HTML-to-PDF锛夛紱APA 7.0 浣跨敤 `apa7` document class锛坄man` 妯″紡锛? XeCJK 鏀彺涓嫳闆欒獮锛涘瓧楂旓細Times New Roman + 鎬濇簮瀹嬮珨 VF + Courier New

### v2.2 / v1.3 (2025-03-05)
- **璺?Agent 鍝佽唱灏嶉綂**锛氱当涓€瀹氱京锛堝悓鍎曞鏌ャ€佹檪鏁堣鍓囥€丆RITICAL 鍤撮噸搴︺€佷締婧愬垎绱氾級姗法鎵€鏈?agent
- **deep-research v2.2**锛歴ynthesis 鍙嶆ā寮忋€佽槆鏍兼媺搴曡嚜鍕曠祼鏉熸浠躲€丏OI+WebSearch 椹楄瓑銆佸挤鍖栧€悊瑾犱俊瀵╂煡銆佹ā寮忚綁鎻涚煩闄?
- **academic-paper v2.2**锛? 绱氳珫璀夊挤搴﹁鍒嗐€佹妱瑗茬鏌ャ€? 鍊嬫柊澶辨晽璺緫锛團11 閫€绋垮京娲汇€丗12 鐮旇◣鏈冭綁鏈熷垔锛夈€丳lan鈫扚ull 妯″紡杞夋彌
- **academic-paper-reviewer v1.3**锛欴A vs R3 瑙掕壊閭婄晫銆丆RITICAL 鍒ゅ畾妯欐簴銆佸叡璀樺垎椤烇紙4/3/SPLIT/DA-CRITICAL锛夈€佷俊蹇冨垎鏁稿姞娆娿€佷簽娲茶垏鍗€鍩熸湡鍒婂弮鑰?
- **academic-pipeline v2.2**锛歝heckpoint 纰鸿獚瑾炴剰銆佹ā寮忓垏鎻涚煩闄ｃ€佹妧鑳藉け鏁楅檷绱氱瓥鐣ャ€佺媭鎱嬫墍鏈夋瑠鍗旇銆佺礌鏉愮増鏈帶鍒?

### v2.0.1 (2026-03)
- **绮剧啊 4 鍊?SKILL.md**锛?371 琛? -16.5%锛夛細绉婚櫎璺?skill 閲嶈銆佸収宓屾ā鏉挎敼鐐烘獢妗堝紩鐢ㄣ€佸啑椁樿矾鐢辫〃銆侀噸瑜囨ā寮忛伕鎿囧崁濉?
- 淇京 academic-paper 鑸?academic-pipeline 涔嬮枔淇▊杩村湀涓婇檺鐨勭煕鐩?

### v2.0 (2026-02)
- **academic-pipeline v2.0**锛?鈫? 闅庢銆佸挤鍒惰獱淇￠璀夈€佸叐闅庢瀵╂煡銆佽槆鏍兼媺搴曚慨瑷傛寚灏庛€佸彲閲嶇従鎬т繚璀?
- **academic-paper-reviewer v1.1**锛?榄旈浠ｈ█浜哄鏌ヨ€咃紙绗?7 agent锛夈€?re-review 妯″紡锛堥鏀讹級銆?瀵╁緦铇囨牸鎷夊簳鎸囧皫
- 鏂板 agent锛歚integrity_verification_agent` 鈥?100% 寮曠敤/鏁告摎椹楄瓑锛屽惈绋芥牳杌岃贰
- 鏂板 agent锛歚devils_advocate_reviewer_agent` 鈥?8 缍害璜栭粸鎸戞埌
- 杓稿嚭闋嗗簭锛歁D 鈫?Pandoc 鍙敤鏅傜敘鍑?DOCX锛堝惁鍓囨彁渚涜鏄庯級鈫?瑭㈠晱 LaTeX 鈫?纰鸿獚 鈫?PDF

### v1.0 (2026-02)
- 鍒濈増鐧煎竷
- deep-research v2.0锛?0 agents銆? 妯″紡鍚?socratic锛?
- academic-paper v2.0锛?0 agents銆? 妯″紡鍚?plan锛?
- academic-paper-reviewer v1.0锛? agents銆? 妯″紡鍚?guided锛?
- academic-pipeline v1.0锛堣搴﹀櫒锛?
