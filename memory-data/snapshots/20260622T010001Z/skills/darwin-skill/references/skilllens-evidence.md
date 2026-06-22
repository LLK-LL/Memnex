# SkillLens 瀹炶瘉鍩虹嚎 + darwin-skill 鏈満楠岃瘉鏁版嵁

> SKILL.md 鍦ㄣ€岃瘎浼?Rubric銆嶇珷鑺備細寮曠敤鏈枃浠躲€傞渶瑕佹煡璁烘枃缁嗚妭銆乧ontrolled study 鏁版嵁銆丠L 瀹炴垬妗堜緥鐨勫叿浣撴暟瀛楁椂璇昏繖閲屻€?
---

## SkillLens 璁烘枃瀹炶瘉锛堝閮ㄨ瘉鎹級

**璁烘枃**锛欶rom Raw Experience to Skill Consumption: A Systematic Study of Model-Generated Agent Skills
**浣滆€?*锛歁icrosoft Research + 澶嶆棪澶у + 涓婃捣浜ゅぇ锛?6 浣滆€咃級
**arXiv**锛?605.23899锛?026-05-22锛屼笌 SkillOpt 鍚屾湡鍙戝竷锛?**瀹為獙瑙勬ā**锛? domains锛圓LFWorld / SpreadsheetBench / SWE-bench-Verified / SEAL-0 / BFCL-v4锛壝?6 targets 脳 5 extractors

### 鍏抽敭鍙戠幇

1. **75% 妗堜緥 skill 鏈夋鏀剁泭锛?5% 鍑虹幇 negative transfer**鈥斺€斿嵆銆屽姞 skill 姣斾笉鍔犺繕宸€?2. **寮?agent 涓嶄竴瀹氭槸濂?extractor**锛圙emini-3.1-FL 鍦?skill 鎻愬彇鏁堢巼涓婂弽瓒?GPT-5.4锛?3. **LLM-as-judge 鍑嗙‘鐜囦粎 46.4%**鈥斺€旂粰 LLM judge 涓や唤 skill锛岃瀹冮€夊摢浠芥洿濂斤紝**姣旀墧纭竵锛?0%锛夎繕宸?*
4. **meta-skill rubric 鎶婂噯纭巼鎻愬崌鍒?73.8%**鈥斺€斿姞鍏ヤ笁涓淮搴︼細
   - **Failure-mechanism encoding**锛堝繀椤绘樉寮忕紪鐮佸け璐ユā寮忥級
   - **Actionable specificity**锛堢姝?鑰冭檻/鍙兘"杞寲鎺緸锛?   - **Risk-action blacklist**锛堝繀椤绘湁鍙嶄緥娓呭崟锛?5. 鎵€鏈?domain 涓€鑷?+1.55pp 鎻愬崌锛坢eta-rubric 涓嶆槸鏌愪釜 domain 鐨勭壒渚嬶級

### 瀵?darwin-skill 鐨勬剰涔?
鏃?8 缁?rubric 鍏ㄩ儴鐢?LLM judge 鎵撳垎 鈫?绯荤粺鎬т箰瑙傚亸宸?鈫?鏈満 results.tsv 鏃╂湡 40 娆?0 revert / 67% dry_run 鍗拌瘉銆?
v2 9 缁?rubric 寮哄寲 dim3/dim5 + 鏂板 dim9 鏄?SkillLens 楠岃瘉杩囩殑鏂瑰悜銆?*浣嗗嵆浣?73.8%锛屾瘡 4 娆″喅绛栦粛閿?1 娆♀€斺€旈噸瑕佸喅绛栧繀椤讳汉瀹＄‘璁ゃ€?*

---

## 鏈満 controlled study锛?026-05-27锛?
### 瀹為獙璁捐

- **鐩爣 skill**锛歨uashu-research锛?70 琛岋紝鐙珛搴﹂珮锛?- **V1**锛氬綋鍓?GitHub 浠撳簱鏈€鏂扮増锛堣 darwin-skill 浼樺寲杩?+33 鍒嗙殑鐗堟湰锛?- **V2 (degraded)**锛氬湪 V1 鍩虹涓婂簲鐢?4 绫绘槑纭川閲忓姡鍖栵細
  - **D1 妯＄硦鍖栧叿浣撴寚浠?*锛氥€屽繀椤?绔嬪嵆銆嶁啋銆屽缓璁?鍙互鏍规嵁鎯呭喌銆?  - **D2 鍒犻櫎鍏抽敭妫€鏌ョ偣**锛氬垹鎺?2 涓?馃敶 妫€鏌ョ偣
  - **D3 鍒犳帀寮傚父澶勭悊琛?*锛氭暣娈点€?# 寮傚父澶勭悊銆嶇珷鑺傚垹闄?  - **D4 鎻掑叆 AI 鑵斿簾璇?*锛氬湪 Step 2銆丼tep 3 鎻掑叆鑺卞彅绂佺敤璇?9 涓璇?- **5 涓嫭绔?judge agent**锛坓eneral-purpose subagent锛屾棤 context 鍏变韩锛夌洸娴嬫墦鍒?- 涓€鍗?judge 鍏堣 V1 鍚庤 V2锛屽彟涓€鍗婂弽搴忥紙鍘婚櫎浣嶇疆鍋忓樊锛?
### 缁撴灉

| Judge | 椤哄簭 | V1 鎬诲垎 | V2 鎬诲垎 | 螖 | Verdict | Confidence |
|---|---|---|---|---|---|---|
| 1 | V1 鈫?V2 | 89.5 | 41.7 | **+47.8** | V1>V2 | high |
| 2 | V2 鈫?V1 | 90.2 | 46.7 | **+43.5** | V1>V2 | high |
| 3 | V1 鈫?V2 | 89.5 | 37.6 | **+51.9** | V1>V2 | high |
| 4 | V2 鈫?V1 | 89.5 | 48.4 | **+41.1** | V1>V2 | high |
| 5 | V1 鈫?V2 | 89.5 | 41.4 | **+48.1** | V1>V2 | high |
| **鍧囧€?* | 鈥?| **89.6** | **43.2** | **+46.5** | **5/5 V1>V2** | **5/5 high** |

### 缁村害绾у叡璇?
| 缁村害 | V1 鍧囧€?| V2 鍧囧€?| 螖 | 涓€鑷存€?|
|---|---|---|---|---|
| 1. Frontmatter | 9.0 | 5.6 | -3.4 | 鍏ㄩ儴璇嗗埆 |
| 2. 宸ヤ綔娴佹竻鏅板害 | 9.0 | 5.0 | -4.0 | 鍏ㄩ儴璇嗗埆 |
| 3. 杈圭晫鏉′欢瑕嗙洊 | 9.2 | 3.4 | -5.8 | **鏈€鏄庢樉鍔ｅ寲** |
| 4. 妫€鏌ョ偣璁捐 | 9.0 | 2.6 | -6.4 | **鏈€鏄庢樉鍔ｅ寲** |
| 5. 鎸囦护鍏蜂綋鎬?| 9.0 | 3.6 | -5.4 | 鍏ㄩ儴璇嗗埆 |
| 6. 璧勬簮鏁村悎搴?| 8.0 | 6.8 | -1.2 | 寮?|
| 7. 鏁翠綋鏋舵瀯 | 9.0 | 4.6 | -4.4 | 鍏ㄩ儴璇嗗埆 |
| 8. 瀹炴祴琛ㄧ幇 | 9.0 | 3.6 | -5.4 | 鍏ㄩ儴璇嗗埆 |

### 缁撹

**rubric 鑳借瘑鍒?gross degradation锛?/5 high confidence锛?*锛屼絾**杩欎笉鑳借瘉鏄?fine-grained quality difference 涔熻兘璇嗗埆**鈥斺€擲killLens 鐨?46.4% 鏉ヨ嚜缁嗙矑搴﹀姣旓紝darwin-skill 鍦ㄧ粏绮掑害鍒ゅ埆涓婁粛鏈夊け鏁堥闄┿€?*閲嶈鍐崇瓥浠嶉渶浜哄銆?*

---

## HL 瀹炴垬 high-leverage 妗堜緥锛堟潵鑷?results.tsv 鐪熷疄璁板綍锛?
### HL-1锛氭樉鎬ц瑙夋爣璁版槸 dim4 鐨勬潬鏉?
**huashu-gpt-image Round 1**锛氱孩绾?4 鏍囬鍓嶅姞 馃敶 CHECKPOINT + 銆岀姝氦浠樸€嶁啋銆岎煕?STOP銆?- 鏀瑰姩锛? 琛?- dim4 鍙樺寲锛?.0 鈫?9.5锛?3.5锛?- 鍗曠淮搴?ROI锛氭瘡琛屾敼鍔?+0.875 鍒?
**huashu-slide-codex r4**锛氳矾寰勪紭鍏堢骇绔犺妭鎻掑叆 馃敶馃敶馃敶 榛樿璺緞閿佸畾閾佸緥
- dim 鎬诲垎 85 鈫?鎸佸钩浣嗛伩鍏嶄簡銆孋odex 鑷垜鍚堢悊鍖栧垏 Path3 澶辫触銆嶅疄娴嬬炕杞?- 瑙嗚閿氭槸 LLM 瑙ｆ瀽鐨勫叧閿俊鍙?
### HL-2锛歩f-then 涓夋寮?fallback 琛?
**huashu-gpt-image Round 1**锛氭柊澧炪€岎煕?澶辫触妯″紡涓?fallback 鏍戙€嶇珷鑺?- 鏀瑰姩锛? 寮犺〃 23 鏉′笁娈靛紡锛堣Е鍙戞潯浠?/ 涓€绾夸慨澶?/ 浠嶅け璐ュ厹搴曪級
  - 鍗曞浘澶辫触 9 鏉?  - 鎵归噺鐢熸垚 9 鏉?  - 鐢熸垚鎵ц灞?5 鏉?- dim3 鍙樺寲锛?.5 鈫?10锛堟弧鍒嗭級

**huashu-weread-advisor edit-r2**锛歋KILL 鍔?11 琛屽叏灞€寮傚父琛?+ 4 琛屾暟鎹睍绀鸿鑼?+ 4 宸ヤ綔娴佸悇鍔?5-6 琛?workflow 鐗规湁寮傚父琛?- 鍏?~33 涓紓甯稿満鏅鐩?- dim 鎬诲垎 81.3 鈫?87.6锛?6.3锛?
### HL-3锛氱淮搴︾浉鍏虫€э紙dim2/3/4 鏄浉鍏崇皣锛?
**huashu-gpt-image 瀹炴祴**锛?- Round 1 鏀?dim3锛堟渶浣?6.5锛夆啋 鏀规垚 10
- 鍚屾湡 dim2 鑷姩浠?7.5 鈫?9锛堟湭鍗曠嫭浼樺寲锛?- Round 2 璇曞浘鍗曠嫭鏀?dim2 鈫?鍙戠幇宸茶Е椤?9锛屽姝や竴涓?- **鏁欒**锛氭壘鏈€浣庣淮搴︽椂鍚屾椂鐪嬬浉鍏崇皣鐭澘

### HL-4锛氳Е椤跺悗杈归檯鏀剁泭閫掑噺

**huashu-gpt-image Round 2**锛?0.15 marginal
- Round 1: +10.7 鍒嗭紙鍩虹嚎 80.8 鈫?91.5锛?- Round 2: +0.15 鍒嗭紙91.5 鈫?91.65锛?- **瑙﹂《淇″彿**锛氳繛缁?2 杞?螖 < 2 鈫?break锛岄伩鍏嶈繃搴︿紭鍖?
**瀵规瘮 darwin-skill 鏃╂湡**锛?0 娆¤褰?0 revert锛岄儴鍒嗘槸鍥犱负娌℃湁瑙﹂《瑙勫垯锛岀‖鍑?MAX_ROUNDS=3 閮?keep 浜嗚竟闄呮敼鍔ㄣ€?
---

## 鍘嗗彶 results.tsv 浼樺寲璁板綍鎽樿锛堟埅鑷?2026-05-27锛?
瀹屾暣璁板綍瑙?`results.tsv`銆?
| skill | 璧峰垎 | 缁堝垎 | 螖 | 妯″紡 |
|---|---|---|---|---|
| huashu-research | 40.0 | 73.2 | +33.2 | dry_run |
| huashu-video-check | 72.1 | 80.5 | +8.4 | dry_run |
| harness-optimizer | 78.4 | 86.0 | +7.6 | dry_run |
| freud-skill | 72.5 | 86.0 | +13.5 | dry_run |
| **claude-design** | **74.5** | **91.0** | **+16.5** | **full_test 鉁?* |
| huashu-design | 62.3 | 86.7 | +24.4 | dry_run |
| huashu-weread-advisor | 76.5 | 91.4 | +14.9 | full_test_informed 鉁?|
| huashu-slide-codex | 82.6 | 85+ | +2~ | mixed |
| **huashu-gpt-image** | **80.8** | **91.65** | **+10.85** | **full_test 鉁咃紙v2 瀹炴垬锛?* |
| **darwin-skill (self-fix)** | **86.05** | **92.05** | **+6.0** | **full_test 鉁咃紙鑷寚闂幆锛?* |

**缁熻**锛?- 骞冲潎鎻愬崌锛殈+13.5 鍒?- 鍏ㄩ儴 keep锛坴1 鏃朵唬 0 revert 鍗拌瘉 rubric 鍋忔澗锛泇2 寮曞叆瑙﹂《 break 瑙勫垯锛?- full_test 姣斾緥锛氫粠 33% 鎻愬崌鍒?100%锛堟渶杩?2 娆￠兘鏄?full_test锛?
