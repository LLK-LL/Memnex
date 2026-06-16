---
name: darwin-skill
description: "Darwin Skill 2.0 (杈惧皵鏂?skill 2.0): autonomous skill optimizer, v2.0 integrates Microsoft Research SkillLens (arXiv 2605.23899) 9-dim rubric + SkillOpt (arXiv 2605.23904) validation-gated design + human-in-the-loop checkpoints. Evaluates SKILL.md files using a 9-dimension rubric (structure + effectiveness + meta-skill blacklists), runs hill-climbing with git version control, spawns independent judge agents for blind evaluation, validates improvements through test prompts with auto-break on diminishing returns, and generates visual result cards. Use when user mentions \"浼樺寲skill\", \"skill璇勫垎\", \"鑷姩浼樺寲\", \"auto optimize\", \"skill璐ㄩ噺妫€鏌", \"杈惧皵鏂嘰", \"darwin\", \"甯垜鏀规敼skill\", \"skill鎬庝箞鏍穃", \"鎻愬崌skill璐ㄩ噺\", \"skill review\", \"skill鎵撳垎\"."
---

# Darwin Skill 2.0

> **v2.0 路 2026-05-28** 鈥?鍚告敹 Microsoft Research SkillLens锛坅rXiv 2605.23899锛夌殑 9 缁磋瘎鍒嗚嵂鏂?+ SkillOpt锛坅rXiv 2605.23904锛夌殑 validation-gated 楠岃瘉鏈哄埗 + human in the loop 涓夊眰瀹堝叧銆?>
> 鍊熼壌 Karpathy autoresearch 鐨勮嚜涓诲疄楠屽惊鐜紝瀵?skills 杩涜鎸佺画浼樺寲銆?> 鏍稿績鐞嗗康锛?*璇勪及 鈫?鏀硅繘 鈫?瀹炴祴楠岃瘉 鈫?浜虹被纭 鈫?淇濈暀鎴栧洖婊?鈫?鐢熸垚鎴愭灉鍗＄墖**
> GitHub: https://github.com/alchaincyf/darwin-skill

---

## 璁捐鍝插

autoresearch 鐨勭簿楂擄細
1. **鍗曚竴鍙紪杈戣祫浜?* 鈥?姣忔鍙敼涓€涓?SKILL.md
2. **鍙岄噸璇勪及** 鈥?缁撴瀯璇勫垎锛堥潤鎬佸垎鏋愶級+ 鏁堟灉楠岃瘉锛堣窇娴嬭瘯鐪嬭緭鍑猴級
3. **妫樿疆鏈哄埗** 鈥?鍙繚鐣欐敼杩涳紝鑷姩鍥炴粴閫€姝?4. **鐙珛璇勫垎** 鈥?璇勫垎鐢ㄥ瓙agent锛岄伩鍏嶃€岃嚜宸辨敼鑷繁璇勩€嶇殑鍋忓樊
5. **浜哄湪鍥炶矾** 鈥?姣忎釜skill浼樺寲瀹屽悗鏆傚仠锛岀敤鎴风‘璁ゅ啀缁х画

涓庣函缁撴瀯瀹℃煡鐨勫尯鍒細涓嶅彧鐪?SKILL.md 鍐欏緱瑙勪笉瑙勮寖锛屾洿鐪嬫敼瀹屽悗**瀹為檯璺戝嚭鏉ョ殑鏁堟灉鏄惁鏇村ソ**銆?
---

## 璇勪及 Rubric锛?缁村害锛屾€诲垎100锛?
> **璁捐渚濇嵁**锛氬熀浜?SkillLens 璁烘枃锛坅rXiv 2605.23899锛夊疄璇佸彂鐜扳€斺€擫LM-as-judge 璇勪及 skill 璐ㄩ噺鍑嗙‘鐜囦粎 46.4%锛堟帴杩戦殢鏈猴級锛屽姞鍏?meta-skill 涓夌淮搴﹀悗鎻愬崌鍒?73.8%銆傛湰 rubric 寮哄寲 dim3 / dim5 璇勫垎鏍囧噯锛屾柊澧?dim9銆屽弽渚嬩笌榛戝悕鍗曘€嶏紝鏉冮噸骞宠　鍒?100銆?*鐩殑锛氳璇勫垎瀵圭湡瀹炶川閲忔洿鏁忔劅锛屽噺灏?LLM judge 鐨勪箰瑙傚亸宸€?*

### 缁撴瀯缁村害锛?9鍒嗭級鈥?闈欐€佸垎鏋?
| # | 缁村害 | 鏉冮噸 | 璇勫垎鏍囧噯 |
|---|------|------|---------|
| 1 | **Frontmatter璐ㄩ噺** | 7 | name瑙勮寖銆乨escription鍖呭惈鍋氫粈涔?浣曟椂鐢?瑙﹀彂璇嶃€佲墹1024瀛楃銆?*绂佺粨灏惧姞"鐏垫椿搴旂敤/鏍规嵁鎯呭喌鍒ゆ柇"绛夌┖璇濆熬宸?* |
| 2 | **宸ヤ綔娴佹竻鏅板害** | 12 | 姝ラ鏄庣‘鍙墽琛屻€佹湁搴忓彿銆佹瘡姝ユ湁鏄庣‘杈撳叆/杈撳嚭 |
| 3 | **澶辫触妯″紡缂栫爜** | 12 | **蹇呴』鏄惧紡缂栫爜澶辫触妯″紡**锛堝啓鍑?濡傛灉 X 澶辫触 鈫?Y"鐨勬槑纭垎鏀級锛涙湁fallback璺緞銆侀敊璇仮澶嶏紱**鍙啓姝ｅ悜娴佺▼鑰屼笉鍐欏け璐ュ垎鏀墸 鈮? 鍒?*锛圫killLens meta-skill 缁村害锛?|
| 4 | **妫€鏌ョ偣璁捐** | 6 | 鍏抽敭鍐崇瓥鍓嶆湁鐢ㄦ埛纭銆侀槻姝㈣嚜涓诲け鎺э紱**妫€鏌ョ偣蹇呴』鏄炬€ф爣璁帮紙馃敶/STOP/CHECKPOINT锛夛紝浠呴潬"濡傛灉...寤鸿..."鎺緸涓嶇畻** |
| 5 | **鍙墽琛屽叿浣撴€?* | 17 | 涓嶆ā绯娿€佹湁鍏蜂綋鍙傛暟/鏍煎紡/绀轰緥銆佸彲鐩存帴鎵ц锛?*绂佹"寤鸿/鍙互鑰冭檻/鏍规嵁鎯呭喌/鐏垫椿鎶婃彙/瑙嗘儏鍐佃€屽畾"绛夎蒋鍖栨帾杈?*鈥斺€斿嚭鐜?鈮? 澶勬墸 鈮? 鍒嗭紙SkillLens actionable specificity 缁村害锛?|
| 6 | **璧勬簮鏁村悎搴?* | 4 | references/scripts/assets寮曠敤姝ｇ‘銆佽矾寰勫彲杈?|

### 鏁堟灉缁村害锛?5鍒嗭級鈥?闇€瑕佸疄娴?
| # | 缁村害 | 鏉冮噸 | 璇勫垎鏍囧噯 |
|---|------|------|---------|
| 7 | **鏁翠綋鏋舵瀯** | 12 | 缁撴瀯灞傛娓呮櫚銆佷笉鍐椾綑涓嶉仐婕忋€佷笌鑺卞彅鐢熸€佷竴鑷达紱**鍐椾綑/AI鑵斿簾璇濇钀斤紙璇寸櫧浜?鎹㈠彞璇濊/棣栧厛鍏舵缁间笂绛夎姳鍙旂鐢ㄨ瘝锛夊嚭鐜颁竴澶勬墸 1 鍒?* |
| 8 | **瀹炴祴琛ㄧ幇** | 23 | 鐢ㄦ祴璇昿rompt璺戜竴閬嶏紝杈撳嚭璐ㄩ噺鏄惁绗﹀悎skill瀹ｇО鐨勮兘鍔?|

### Meta-skill 缁村害锛?鍒嗭級鈥?鍙嶄緥涓庨粦鍚嶅崟

| # | 缁村害 | 鏉冮噸 | 璇勫垎鏍囧噯 |
|---|------|------|---------|
| 9 | **鍙嶄緥涓庨粦鍚嶅崟** | 6 | **skill 蹇呴』鏈?涓嶈鍋氫粈涔?鐨勫弽渚嬫竻鍗?*锛涘彧鍐?搴旇鍋?X"娌℃湁"涓嶈鍋?Y"鎵?鈮? 鍒嗭紱绾㈢伅/鍗遍櫓鍔ㄤ綔/鍙嶆ā寮忓簲鍗曠嫭绔犺妭鍒楀嚭锛圫killLens risk-action blacklist 缁村害锛?|

### 璇勫垎瑙勫垯
- 缁村害1-7銆?锛氭瘡涓淮搴︽墦 1-10 鍒嗭紝涔樹互鏉冮噸寰楀埌璇ョ淮搴﹀緱鍒?- 缁村害8锛堝疄娴嬭〃鐜帮級锛氳窇2-3涓祴璇昿rompt锛屾寜杈撳嚭璐ㄩ噺鎵?-10鍒?- **鎬诲垎 = 危(缁村害鍒?脳 鏉冮噸) / 10**锛屾弧鍒?00
- 鏀硅繘鍚庢€诲垎蹇呴』 **涓ユ牸楂樹簬** 鏀硅繘鍓嶆墠淇濈暀

### Rubric 鐨勫疄璇佸熀纭€

rubric 璁捐渚濇嵁鏉ヨ嚜 **SkillLens 璁烘枃锛坅rXiv 2605.23899锛?* + **鏈満 controlled study**锛?
- SkillLens 鍙戠幇 LLM-as-judge 鍑嗙‘鐜囦粎 46.4%锛堟帴杩戦殢鏈猴級锛屽姞鍏?meta-skill 涓夌淮搴﹀悗鍗囧埌 73.8%
- 鏈満瀵?huashu-research 鍋?4 绫?degradation 鈫?5 涓嫭绔?judge 鐩叉祴涓€鑷?V1>V2锛屛?鍧囧€?+46.5锛?/5 high confidence锛?
**缁撹**锛歳ubric 鑳借瘑鍒?gross degradation锛屼絾 fine-grained quality difference 浠嶄笉鍙俊锛?*閲嶈鍐崇瓥蹇呴』浜哄**銆?
鈫?璇︾粏璁烘枃璇佹嵁 + 5 judges 瀹屾暣鏁版嵁 + HL 瀹炴垬妗堜緥鏁板瓧瑙?[references/skilllens-evidence.md](references/skilllens-evidence.md)

### 鍏充簬銆屽疄娴嬭〃鐜般€嶇淮搴?
杩欐槸涓庣函缁撴瀯璇勫垎鏈€澶х殑鍖哄埆銆傝瘎鍒嗘柟寮忥細

1. 涓烘瘡涓猻kill璁捐2-3涓?*鍏稿瀷鐢ㄦ埛prompt**锛堜笉鏄竟缂榗ase锛屾槸鏈€甯歌鐨勪娇鐢ㄥ満鏅級
2. 鐢ㄥ瓙agent鎵ц锛氫竴涓甫skill璺戯紝涓€涓笉甯kill璺戯紙baseline锛?3. 瀵规瘮杈撳嚭璐ㄩ噺锛屼粠浠ヤ笅瑙掑害鎵撳垎锛?   - 杈撳嚭鏄惁瀹屾垚浜嗙敤鎴锋剰鍥撅紵
   - 鐩告瘮涓嶅甫skill鐨刡aseline锛岃川閲忔彁鍗囨槑鏄惧悧锛?   - 鏈夋病鏈塻kill寮曞叆鐨勮礋闈㈠奖鍝嶏紙杩囧害鍐椾綑銆佽窇鍋忋€佹牸寮忓鎬級锛?
鑻ュ瓙 agent 涓嶅彲鐢紙瓒呮椂/璧勬簮闄愬埗锛夛紝閫€鍖栦负銆屽共璺戦獙璇併€嶏細璇诲畬 skill 鍚庢ā鎷熶竴涓吀鍨?prompt 鐨勬墽琛屾€濊矾锛屽垽鏂祦绋嬫槸鍚﹀悎鐞嗭紱蹇呴』鍦?results.tsv 鏍囨敞 `dry_run`銆?*dry_run 姣斾緥 > 30% 鈫?璇勪及澶辨晥璀﹀憡**锛堟潵鑷湰鏈?controlled study锛歞im8 瀹炴祴缁村害鏉冮噸 23%锛屾棤 full_test 楠岃瘉鏃跺垎鏁颁笉鍙俊锛夈€?
---

## Runtime 閫傞厤鎬у鏌ワ紙gate 椤癸紝鐙珛浜?9 缁村害璇勫垎锛?
skill 搴斿綋鑳藉湪 Claude Code / Codex / Cursor / OpenClaw / Hermes / Gemini CLI / OpenCode 绛?50+ skills-compatible runtime 閫氱敤鈥斺€斿惁鍒欏叾浠?agent 瑙ｆ瀽鏃朵細琚€屽湪 Claude Code 閲屻€嶃€孋laude Code skill銆嶇瓑鎺緸璇垽涓恒€屼笉鏄粰鎴戠敤鐨勩€嶇洿鎺ユ嫆瑁咃紙瀹炰緥锛歯uwa-skill 鍥犳琚?Marvis agent 鎷掔粷锛夈€?
### Phase 1 鍩虹嚎璇勪及鏃跺己鍒惰窇涓€娆＄孩鐏壂鎻?
```bash
grep -nE "(鍦?Claude Code|Claude Code skill|Claude Code 鐢ㄦ埛|Cursor only|Codex 涓瓅^\[!\[Claude Code|~/\.claude/skills/[a-z]|/plugin install\b)" SKILL.md README.md 2>/dev/null
```

杈撳嚭闈炵┖ = 绾㈢伅鍛戒腑 鈫?寮哄埗鎶?Phase 2 绗竴杞畾涓?P0銆宺untime drift 淇銆嶏紙鍐欏叆 results.tsv 鐨?note 鍒?`runtime_warn=N`锛夈€?
### 渚嬪锛堝厑璁哥殑銆孋laude Code 鐥曡抗銆嶏級

frontmatter 瑙﹀彂璇嶃€佽姳鍙旂敓鎬佸唴閮?skill 鍚嶅紩鐢ㄣ€佹槑纭爣娉?runtime-specific 绔犺妭銆乧ommit message鈥斺€旇繖浜涙褰撳嚭鐜帮紝涓嶇畻绾㈢伅銆?
鈫?绾㈢伅/缁跨伅瀹屾暣瀵圭収琛?+ 渚嬪娓呭崟璇︾粏瑙勫垯 + Phase 1/2/3 鍚勯樁娈靛鏌ユ椂鏈鸿 [references/runtime-neutrality.md](references/runtime-neutrality.md)

---

## 鑷富浼樺寲寰幆

### Phase 0: 鍒濆鍖?
```
1. 纭浼樺寲鑼冨洿锛?   - 鍏ㄩ儴skills 鈫?鎵弿 .claude/skills/*/SKILL.md
   - 鎸囧畾skills 鈫?鐢ㄦ埛鎸囧畾鍒楄〃
2. 鍒涘缓 git 鍒嗘敮锛歛uto-optimize/YYYYMMDD-HHMM
3. 鍒濆鍖?results.tsv锛堝涓嶅瓨鍦級
4. 璇诲彇鐜版湁 results.tsv 浜嗚В鍘嗗彶浼樺寲璁板綍
```

### Phase 0.5: 娴嬭瘯Prompt璁捐

鍦ㄨ瘎浼颁箣鍓嶏紝涓烘瘡涓猻kill璁捐娴嬭瘯prompt銆傝繖姝ュ緢鍏抽敭鈥斺€旀病鏈夋祴璇昿rompt锛屻€屽疄娴嬭〃鐜般€嶇淮搴﹀氨鎵撲笉浜嗗垎銆?
```
for each skill:
  1. 璇诲彇 SKILL.md锛岀悊瑙ｅ畠鍋氫粈涔?  2. 璁捐2-3涓祴璇昿rompt锛岃鐩栵細
     - 鏈€鍏稿瀷鐨勪娇鐢ㄥ満鏅紙happy path锛?     - 涓€涓◢澶嶆潅鎴栨湁姝т箟鐨勫満鏅?  3. 淇濆瓨鍒?skill鐩綍/test-prompts.json锛?     [
       {"id": 1, "prompt": "鐢ㄦ埛浼氳鐨勮瘽", "expected": "鏈熸湜杈撳嚭鐨勭畝鐭弿杩?},
       {"id": 2, "prompt": "...", "expected": "..."}
     ]
```

灞曠ず鎵€鏈夋祴璇昿rompt缁欑敤鎴凤紝**纭鍚庡啀杩涘叆璇勪及**銆傛祴璇昿rompt鐨勮川閲忓喅瀹氫簡浼樺寲鏂瑰悜鏄惁姝ｇ‘銆?
### Phase 1: 鍩虹嚎璇勪及锛圔aseline锛?
```
for each skill in 浼樺寲鑼冨洿:

  # 缁撴瀯璇勫垎锛堜富agent鍙互鍋氾級
  1. 璇诲彇 SKILL.md 鍏ㄦ枃
  2. 鎸夌淮搴?-7閫愰」鎵撳垎锛堥檮绠€鐭悊鐢憋級

  # 鏁堟灉璇勫垎锛堢敤瀛恆gent鍋氾紝鐙珛浜庝富agent锛?  3. 瀵规瘡涓祴璇昿rompt锛宻pawn瀛恆gent锛?     - with_skill: 甯︾潃SKILL.md鎵ц娴嬭瘯prompt
     - baseline: 涓嶅甫skill鎵ц鍚屼竴prompt
  4. 瀵规瘮涓ょ粍杈撳嚭锛屾墦缁村害8鐨勫垎

  # 姹囨€?  5. 璁＄畻鍔犳潈鎬诲垎
  6. 璁板綍鍒?results.tsv
```

**濡傛灉瀛恆gent涓嶅彲鐢?*锛堣秴鏃躲€佺幆澧冮檺鍒讹級锛岀淮搴?鐢ㄥ共璺戦獙璇佹墦鍒嗭紝鏍囨敞 `dry_run`銆備笉瑕佸洜涓鸿窇涓嶄簡娴嬭瘯灏辫烦杩囪繖涓淮搴︹€斺€斿摢鎬曟槸妯℃嫙鎺ㄦ紨涔熸瘮瀹屽叏涓嶇湅鏁堟灉濂姐€?
鍩虹嚎璇勪及瀹屾垚鍚庯紝灞曠ず璇勫垎鍗★細

```
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?Skill                    鈹?Score 鈹?缁撴瀯鐭澘      鈹?鏁堟灉鐭澘      鈹?鈹溾攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?huashu-proofreading      鈹?78    鈹?杈圭晫鏉′欢      鈹?娴嬭瘯prompt2  鈹?鈹?huashu-slides            鈹?72    鈹?鎸囦护鍏蜂綋鎬?   鈹?baseline鎸佸钩  鈹?鈹溾攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?骞冲潎                     鈹?75    鈹?             鈹?             鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹粹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹粹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹粹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?```

**馃敶 CHECKPOINT 路 馃洃 STOP锛氭殏鍋滅瓑鐢ㄦ埛纭锛屽啀杩涘叆浼樺寲寰幆銆?*

### Phase 2: 浼樺寲寰幆

鐢ㄦ埛纭鍚庯紝鎸夊熀绾垮垎鏁颁粠浣庡埌楂樻帓搴忥紝鍏堜紭鍖栨渶寮辩殑銆?
```
for each skill:
  round = 0
  while round < MAX_ROUNDS (榛樿3):
    round += 1

    # Step 1: 璇婃柇
    鎵惧嚭寰楀垎鏈€浣庣殑缁村害锛堢粨鏋勬垨鏁堟灉閮界畻锛?    # HL-3 璀﹀憡锛歞im2/dim3/dim4 鏄浉鍏崇皣锛屼慨涓€涓椂鍙︿袱涓父璺熺潃娑?    # 鈫?涓嶈鍥犱负 dim3 鏈€浣庡氨鍗曠嫭淇紝瑕佺湅鏁寸皣鐭澘鍐嶅喅瀹氭槸鍚﹀悓姝ユ敼

    # Step 2: 鎻愬嚭鏀硅繘鏂规
    閽堝鏈€浣庣淮搴︼紝鐢熸垚1涓叿浣撴敼杩涙柟妗堬細
      - 鏀逛粈涔堬紙鍏蜂綋娈佃惤/琛岋級
      - 涓轰粈涔堟敼锛堝搴攔ubric鍝潯锛?      - 棰勬湡鎻愬崌澶氬皯鍒?
    # Step 3: 鎵ц鏀硅繘
    缂栬緫 SKILL.md
    git add + commit锛坢essage: "optimize {skill}: {鏀硅繘鎽樿}"锛?
    # Step 4: 閲嶆柊璇勪及
    - 缁撴瀯缁村害锛氫富agent閲嶆柊鎵撳垎
    - 鏁堟灉缁村害锛歴pawn鐙珛瀛恆gent閲嶈窇娴嬭瘯prompt锛堝叧閿紒涓嶈兘鑷繁璇勮嚜宸憋級

    # Step 5: 鍐崇瓥
    if 鏂版€诲垎 > 鏃ф€诲垎:
      status = "keep"锛屾洿鏂版棫鎬诲垎
      # HL-4 瑙佸ソ灏辨敹锛氳繛缁?杞?螖 < 2 鍒?鈫?break 杩?Phase 3
      if last_delta < 2.0 and this_delta < 2.0:
        print("瑙﹂《淇″彿锛氳繛缁?杞竟闄呮敹鐩?< 2 鍒嗭紝鍋滄浼樺寲閬垮厤杩囧害璋冩暣")
        break
    else:
      status = "revert"
      git revert HEAD锛堝垱寤烘柊commit鍥炴粴锛屼笉鐢╮eset --hard锛?      璁板綍澶辫触灏濊瘯鍒?results.tsv
      break  # 璇kill鍒扮摱棰堬紝璺冲埌涓嬩竴涓?
    # Step 6: 鏃ュ織
    results.tsv 杩藉姞琛?
  # === 馃敶 CHECKPOINT 路 姣忎釜 skill 浼樺寲瀹屽悗寮哄埗浜哄 ===
  灞曠ず璇kill鐨勬敼鍔ㄦ憳瑕侊細
    - git diff锛堟敼鍓?vs 鏀瑰悗锛?    - 鍒嗘暟鍙樺寲锛堝摢浜涚淮搴︽彁鍗?涓嬮檷锛?    - 娴嬭瘯prompt杈撳嚭瀵规瘮锛堝鏋滆窇杩囩殑璇濓級
  绛夌敤鎴风‘璁?OK 鍐嶇户缁笅涓€涓猻kill銆?  濡傛灉鐢ㄦ埛璇?涓嶅ソ"锛屽洖婊氬埌璇kill鐨勪紭鍖栧墠鐗堟湰銆?```

### Phase 2.5: 鎺㈢储鎬ч噸鍐欙紙鎸夐渶瑙﹀彂锛?
褰?hill-climbing 杩炵画2涓猻kill閮藉湪 round 1 灏?break锛堟定涓嶅姩锛夋椂锛屾彁璁竴娆°€屾帰绱㈡€ч噸鍐欍€嶏細

```
1. 閫変竴涓摱棰坰kill
2. git stash 淇濆瓨褰撳墠鏈€浼樼増鏈?3. 浠庡ご閲嶅啓SKILL.md锛堜笉鏄井璋冿紝鏄噸鏂扮粍缁囩粨鏋勫拰琛ㄨ揪鏂瑰紡锛?4. 閲嶆柊璇勪及
5. if 閲嶅啓鐗?> stash鐗? 閲囩敤閲嶅啓鐗?   else: git stash pop 鎭㈠
```

杩欒В鍐充簡 hill-climbing 鐨勫眬閮ㄦ渶浼橀棶棰樷€斺€旀湁鏃跺€欓渶瑕併€屽厛鎷嗗悗寤恒€嶆墠鑳界獊鐮寸摱棰堛€?**馃敶 CHECKPOINT 路 馃洃 STOP锛氬繀椤诲緛寰楃敤鎴峰悓鎰忓悗鎵嶆墽琛屻€?*

### Phase 3: 姹囨€绘姤鍛?
```
## 浼樺寲鎶ュ憡

### 鎬昏
- 浼樺寲skills鏁帮細N
- 鎬诲疄楠屾鏁帮細M
- 淇濈暀鏀硅繘锛歑锛圷%锛?- 鍥炴粴娆℃暟锛歓
- 瀹炴祴楠岃瘉锛欰娆″畬鏁存祴璇?/ B娆″共璺?
### 鍒嗘暟鍙樺寲
鈹屸攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?Skill                    鈹?Before 鈹?After  鈹?螖      鈹?鈹溾攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?huashu-proofreading      鈹?78     鈹?87     鈹?+9     鈹?鈹?huashu-slides            鈹?72     鈹?83     鈹?+11    鈹?鈹溾攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹尖攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?鈹?骞冲潎                     鈹?75     鈹?85     鈹?+10    鈹?鈹斺攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹粹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹粹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹粹攢鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹?
### 涓昏鏀硅繘
1. [skill-A] 琛ュ厖浜嗚竟鐣屾潯浠跺鐞嗭紝娴嬭瘯杈撳嚭璐ㄩ噺鎻愬崌鏄庢樉
2. [skill-B] 閲嶇粍浜唚orkflow缁撴瀯锛宐aseline瀵规瘮浼樺娍澧炲ぇ
```

---

## results.tsv 鏍煎紡

```tsv
timestamp	commit	skill	old_score	new_score	status	dimension	note	eval_mode
2026-03-31T10:00	baseline	huashu-proofreading	-	78	baseline	-	鍒濆璇勪及	full_test
2026-03-31T10:05	a1b2c3d	huashu-proofreading	78	84	keep	杈圭晫鏉′欢	琛ュ厖fallback	full_test
2026-03-31T10:10	b2c3d4e	huashu-proofreading	84	82	revert	鎸囦护鍏蜂綋鎬?杩囧害缁嗗寲	dry_run
```

鏂板 `eval_mode` 鍒楋細`full_test`锛堣窇浜嗗瓙agent娴嬭瘯锛夋垨 `dry_run`锛堟ā鎷熸帹婕旓級銆?鏂囦欢浣嶇疆锛歚.claude/skills/darwin-skill/results.tsv`

---

## 瀹炴垬 high-leverage 鎿嶄綔锛堢簿楂撻€熸煡锛?
4 鏉＄粡瀹炴垬楠岃瘉锛坔uashu-gpt-image +10.85 / huashu-weread-advisor +14.9 / claude-design +16.5锛夈€傝缁嗘渚嬫暟鎹 [references/skilllens-evidence.md](references/skilllens-evidence.md) 鐨勩€孒L 瀹炴垬妗堜緥銆嶈妭銆?
- **HL-1锛坉im4锛夋樉鎬ц瑙夋爣璁版槸鏉犳潌**锛氬姞 馃敶 CHECKPOINT / 馃洃 STOP锛岄潬銆屽繀椤汇€嶆帾杈炰笉琛屸€斺€擫LM 瑙ｆ瀽鏃舵壂鎻忚瑙夋爣璁般€? 琛屾敼鍔ㄦ挰鍔?dim4 +3 鍒?- **HL-2锛坉im3锛塱f-then 涓夋寮?fallback 琛?*锛氭妸銆岀棁鐘?瑙ｆ硶銆嶄袱鍒楀崌绾т负銆岃Е鍙戞潯浠?/ 涓€绾夸慨澶?/ 浠嶅け璐ュ厹搴曘€嶄笁娈靛紡銆係killLens failure-mechanism encoding 缁村害鐨勮惤鍦?- **HL-3锛圥hase 2 璇婃柇锛夌淮搴︾浉鍏崇皣璀﹀憡**锛歞im2/3/4 鏄浉鍏崇皣鈥斺€斾慨 dim3 鏃?dim2 甯歌窡鐫€娑ㄣ€傘€屾壘鏈€浣庣淮搴︺€嶆椂鍚屾椂鐪嬬浉鍏崇皣鐭澘鍐嶅喅瀹氭槸鍚﹀悓姝ユ敼
- **HL-4锛圥hase 2 閫€鍑猴級瑙﹂《鑷姩 break**锛氳繛缁?2 杞?螖 < 2 鍒?鈫?break 杩?Phase 3銆?0.15 鏄仠鎵嬩俊鍙蜂笉鏄户缁俊鍙凤紱纭噾 MAX_ROUNDS=3 寮曞叆 over-engineering

---

## 浼樺寲绛栫暐搴?
鎸変紭鍏堢骇鎺掑簭锛屾瘡杞彧鍋氭渶楂樹紭鍏堢骇鐨勪竴涓細

### P0: Runtime 閫傞厤鎬ч棶棰橈紙gate 椤瑰懡涓?鈫?蹇呴』鍏堜慨锛?- README/SKILL.md 鍑虹幇绾㈢伅鎺緸锛堝銆屽湪 Claude Code 閲屻€嶃€孋laude Code skill銆嶏級鈫?鏇挎崲涓?runtime-neutral 鎺緸
- Badge 閽夋鍗曚竴 runtime 鈫?鏀逛负 `Agent Skills Standard` + `skills.sh` + `Multi-Runtime` 涓変釜涓珛 badge
- 瀹夎绔犺妭鍙粰涓€绉?runtime 鐨勮矾寰?鈫?鏀逛负銆屼竴琛屽懡浠わ紙auto-detect锛? 鎵嬪姩璺緞琛?+ 浣滀负鍙傝€冭祫鏂欍€嶄笁灞傜粨鏋?- 宸ヤ綔娴佺‖缂栫爜 runtime-specific 宸ュ叿涓旀棤 fallback 鈫?缁欏嚭閫氱敤鏇夸唬鏂规鎴栨爣娉ㄣ€屼粎鍦ㄦ煇 runtime 鍙敤銆?- 渚嬪锛歴kill 鍚嶆槑纭爣娉ㄥ崟 runtime锛堝 `xxx-codex`锛夌殑锛屽彲璺宠繃鏈」

### P0: 鏁堟灉闂锛堝疄娴嬪彂鐜扮殑锛?- 娴嬭瘯杈撳嚭鍋忕鐢ㄦ埛鎰忓浘 鈫?妫€鏌kill鏄惁鏈夎瀵兼€ф寚浠?- 甯kill姣斾笉甯﹁繕宸?鈫?skill鍙兘杩囧害绾︽潫锛岃€冭檻绮剧畝
- 杈撳嚭鏍煎紡涓嶇鍚堥鏈?鈫?琛ュ厖鏄庣‘鐨勮緭鍑烘ā鏉?
### P1: 缁撴瀯鎬ч棶棰?- Frontmatter缂哄皯瑙﹀彂璇?鈫?琛ュ厖涓嫳鏂囪Е鍙戣瘝
- 缂哄皯Phase/Step缁撴瀯 鈫?閲嶇粍涓虹嚎鎬ф祦绋?- 缂哄皯鐢ㄦ埛纭妫€鏌ョ偣 鈫?鍦ㄥ叧閿喅绛栧鎻掑叆

### P2: 鍏蜂綋鎬ч棶棰?- 姝ラ妯＄硦锛?澶勭悊鍥剧墖"锛夆啋 鏀逛负鍏蜂綋鎿嶄綔鍜屽弬鏁?- 缂哄皯杈撳叆/杈撳嚭瑙勬牸 鈫?琛ュ厖鏍煎紡銆佽矾寰勩€佺ず渚?- 缂哄皯寮傚父澶勭悊 鈫?琛ュ厖 "濡傛灉X澶辫触锛屽垯Y"

### P3: 鍙鎬ч棶棰?- 娈佃惤杩囬暱 鈫?鎷嗗垎+鐢ㄨ〃鏍?- 閲嶅鎻忚堪 鈫?鍚堝苟鍘婚噸
- 缂哄皯閫熸煡 鈫?娣诲姞TL;DR鎴栧喅绛栨爲

---

## 寮傚父涓庤竟鐣屾潯浠?
娴佺▼鍋囪鐜鐞嗘兂锛屼絾瀹炴搷甯搁亣寮傚父銆備互涓嬮瀹氫箟 fallback锛屼繚璇佷紭鍖栬繃绋嬩笉浼氥€屼竴璺戝氨鍗′綇銆嶃€?
| 鍦烘櫙 | 瑙﹀彂鏉′欢 | 澶勭悊鍔ㄤ綔 |
|---|---|---|
| 涓嶅湪 git 浠撳簱 | `git rev-parse` 澶辫触 | 璇㈤棶鐢ㄦ埛锛氭墽琛?`git init` 鎴栧洖閫€鍒版枃浠跺浠斤紱鐢ㄦ埛閫夊悗鑰呭垯 `cp SKILL.md SKILL.md.bak.YYYYMMDD-HHMM` 浠ｆ浛 revert |
| results.tsv 缂哄け | 鏂囦欢涓嶅瓨鍦?| 鏂板缓骞跺啓琛ㄥご琛岋紙9鍒楋細鍚?eval_mode锛?|
| results.tsv 鎹熷潖 | 鍒楁暟涓嶅尮閰?/ 闈濼SV | 澶囦唤涓?`.bak.YYYYMMDD-HHMM` 鍚庨噸寤猴紝鍛婄煡鐢ㄦ埛 |
| 鍒嗘敮宸插瓨鍦?| `git checkout -b` 澶辫触 | 鍒嗘敮鍚嶆湯灏惧姞 `-2` / `-3`锛涚3娆″け璐ュ垯鍒囧洖鐜版湁鍒嗘敮骞惰闂户缁繕鏄柊璧?|
| `git revert` 澶辫触 | 鍐茬獊 / 宸ヤ綔鏍戣剰 | 鍏?`git stash`锛岄噸璇曪紱浠嶅け璐ュ垯浠庝笂涓€涓?commit 鐨?SKILL.md 璇诲嚭瑕嗙洊褰撳墠鏂囦欢鎵嬪姩鎭㈠ |
| MAX_ROUNDS 瑙﹂《锛堥粯璁?锛?| 宸茶窇3杞粛鏈夌煭鏉?| 涓嶅己鍒?break锛屽睍绀哄綋鍓嶆渶寮辩淮搴﹂棶鐢ㄦ埛銆岀户缁姞1杞?/ 杩涘叆Phase 2.5 / 鏀跺伐銆?|
| 浼樺寲鍚庤秴 150% 浣撶Н | 鏂版枃浠?> 鍘?脳 1.5 | 鎷掔粷鎻愪氦锛屽洖鍒版敼杩涙楠ょ簿绠€锛堝垹鍐椾綑/鍚堝苟閲嶅锛夛紝鍐嶈瘎 |
| test-prompts.json 宸插瓨鍦?| 鏂囦欢宸插湪 skill 鐩綍 | 榛樿澶嶇敤骞跺睍绀猴紝闂敤鎴枫€屽鐢?/ 閲嶅啓 / 杩藉姞銆嶄笁閫変竴 |
| SKILL.md 鎵句笉鍒?| 鐩綍瀛樺湪浣嗘棤 SKILL.md | 璇?skill 缁堟锛宺esults.tsv 璁?`status=error`锛岀户缁笅涓€涓?|
| 鍒嗘暟璁＄畻瑙勫垯 | 娴偣绮惧害婕傜Щ | 鎬诲垎淇濈暀 1 浣嶅皬鏁帮紝鏀硅繘闇€涓ユ牸 > 鏃у垎锛堜笉闈犲洓鑸嶄簲鍏ワ級 |

**鍘熷垯**锛氬紓甯稿厛鍛婄煡鐢ㄦ埛锛屽啀鎸夎鍒欏鐞嗭紱缁濅笉闈欓粯璺宠繃鎴栭潤榛樺け璐ャ€?
---

## darwin 鎿嶄綔鍙嶄緥榛戝悕鍗曪紙dim9 搴旂敤锛歞arwin 鑷繁浼樺寲鏃朵笉瑕佸仛鐨勪簨锛?
鏉ヨ嚜鏈満 results.tsv 鏃╂湡 40 娆?0 revert 鐨勬暀璁?+ Judge G/H 鑷寚璇勪及鏆撮湶鐨勫弽妯″紡銆傛瘡鏉￠兘鏄?*鐪熷疄韪╄繃鐨勫潙**銆?
| # | 鍙嶆ā寮?| 涓轰粈涔堜笉瑕佸仛 | 鏇夸唬鍋氭硶 |
|---|---|---|---|
# REDACTED: sensitive-looking memory line
| 2 | **`git reset --hard` 褰撳洖婊?* | 浼氫涪宸ヤ綔鏍戞湭鎻愪氦鏀瑰姩锛汣I 鍘嗗彶鏂 | 鐢?`git revert HEAD` 鍒涘缓鍙嶅悜 commit锛屼繚鐣欏彲杩芥函閾?|
| 3 | **涓哄噾鍒嗗鍐椾綑** | 瑙﹂《鍚庣户缁‖鏀瑰線寰€鏄€屽姞搴熻瘽/鍔犳钀借 LLM 瑙夊緱鏇磋缁嗐€嶏紝瀹為檯璐ㄩ噺涓嶅彉 | 瑙﹂《淇″彿锛堣繛缁?2 杞?螖<2 鍒嗭級鈫?break 杩?Phase 3锛?*瑙佸ソ灏辨敹** |
| 4 | **璺宠繃 test-prompts 鐩存帴璇勫垎** | 娌℃湁 test-prompts 鐨?dim8 鏄嚟绌烘墦鍒嗭紝鏉冮噸 23% 绛変簬缂栭€?| Phase 0.5 寮哄埗璁捐 2-3 prompts锛涜嫢鐢ㄦ埛涓嶇粰锛岄粯璁ょ紪 3 涓苟灞曠ず纭 |
| 5 | **杞唴鏀瑰涓淮搴?* | 澶氬彉閲忓悓鏃跺彉锛屽垎鏁板崌闄嶆棤娉曞綊鍥犲埌鍏蜂綋鏀瑰姩 | 姣忚疆 1 涓淮搴︼紱鐩稿叧绨囷紙dim2/3/4锛夋敼鍏朵竴鏃惰瀵熷彟涓や釜鏄惁璺熸定 |
| 6 | **dry_run 姣斾緥 > 30%** | dim8 瀹炴祴缁村害褰㈠悓铏氳锛屽垎鏁拌櫄楂橈紙鏃╂湡 40 娆¤褰?67% dry_run锛? revert锛?| 寮哄埗鑷冲皯 1 涓湡瀹?full_test锛沝ry_run 澶氱殑浼樺寲鍦?results.tsv 鏄惧紡鎵?鈿狅笍 |
| 7 | **闈欓粯璺宠繃寮傚父** | 閬囧埌 git/tsv 寮傚父鏃堕潤榛樼户缁紝鐮村潖 ratchet 瀹屾暣鎬?| 寮傚父琛?10 鏉?fallback 蹇呴』鍏堝憡鐭ョ敤鎴峰啀澶勭悊 |
| 8 | **蹇借缁村害鐩稿叧鎬у崟鐙紭鍖?* | dim2/3/4 鏄浉鍏崇皣锛屽崟鐙紭鍖?dim2 鏃跺父鍙戠幇宸茶鍓嶈疆 dim3 淇鎺ㄥ埌椤?| 鎵炬渶浣庣淮搴︽椂鍚屾椂鐪嬬浉鍏崇皣鐭澘锛屽喅瀹氭槸鍚﹀悓姝ユ敼 |

**瑙﹀彂鍦烘櫙**锛氭瘡杞?Phase 2 鏀瑰姩鍓嶅鐓ф湰琛ㄤ竴娆°€備换涓€鍙嶆ā寮忓懡涓?鈫?鏀规柟妗堥噸鍐欍€?
---

## 绾︽潫瑙勫垯

1. **涓嶆敼鍙榮kill鐨勬牳蹇冨姛鑳藉拰鐢ㄩ€?* 鈥?鍙紭鍖?鎬庝箞鍐?鍜?鎬庝箞鎵ц"锛屼笉鏀?鍋氫粈涔?
2. **涓嶅紩鍏ユ柊渚濊禆** 鈥?涓嶆坊鍔爏kill鍘熸湰娌℃湁鐨剆cripts鎴杛eferences鏂囦欢
3. **姣忚疆鍙敼涓€涓淮搴?* 鈥?閬垮厤澶氫釜鍙樻洿瀵艰嚧鏃犳硶褰掑洜
4. **淇濇寔鏂囦欢澶у皬鍚堢悊** 鈥?浼樺寲鍚嶴KILL.md涓嶅簲瓒呰繃鍘熷澶у皬鐨?50%
5. **灏婇噸鑺卞彅椋庢牸** 鈥?涓枃涓轰富銆佺畝娲佷负涓?6. **鍙洖婊?* 鈥?鎵€鏈夋敼鍔ㄥ湪git鍒嗘敮涓婏紝鐢╣it revert鑰岄潪reset --hard
7. **璇勫垎鐙珛鎬?* 鈥?鏁堟灉缁村害蹇呴』鐢ㄥ瓙agent鎴栬嚦灏戝共璺戦獙璇侊紝涓嶈兘鍦ㄥ悓涓€涓婁笅鏂囬噷銆屾敼瀹岀洿鎺ヨ瘎銆?8. **Runtime 涓珛鎬?* 鈥?skill 蹇呴』鑳藉湪 Claude Code銆丆odex銆丆ursor銆丱penClaw銆丠ermes 绛変换浣?skills-compatible runtime 涓甯歌繍琛屻€傞櫎闈?skill 鍚嶆槑纭粦瀹氬崟涓€ runtime锛堝 `xxx-codex`銆乣huashu-slides-codex`锛夛紝浠讳綍銆屽湪 Claude Code 閲屻€嶃€孋laude Code skill銆嶃€屽崟涓€ badge 閽夋銆嶃€屽畨瑁呭懡浠ゅ彧缁?`.claude/skills/` 涓€绉嶈矾寰勩€嶉兘瑙嗕负 gate 涓嶉€氳繃锛岄』鍦?P0 浼樺厛淇锛堣瑙併€孯untime 閫傞厤鎬у鏌ャ€嶇珷鑺傦級

---

## 浣跨敤鏂瑰紡

### 鍏ㄩ噺浼樺寲锛堟帹鑽愰娆′娇鐢級
```
鐢ㄦ埛锛?浼樺寲鎵€鏈塻kills"
鈫?Phase 0-3 瀹屾暣娴佺▼
鈫?榛樿锛氬厛鍩虹嚎璇勪及锛屾寜鍒嗘暟鍗囧簭浼樺厛浼樺寲鏈€浣?5-10 涓?```

### 鍗曚釜浼樺寲
```
鐢ㄦ埛锛?浼樺寲 huashu-slides 杩欎釜skill"
鈫?鍙鎸囧畾skill鎵ц Phase 0.5-2
```

### 浠呰瘎浼颁笉鏀?```
鐢ㄦ埛锛?璇勪及鎵€鏈塻kills鐨勮川閲?
鈫?鍙墽琛?Phase 0.5-1锛堣璁℃祴璇昿rompt + 鍩虹嚎璇勪及锛夛紝涓嶈繘鍏ヤ紭鍖栧惊鐜?```

### 鏌ョ湅鍘嗗彶
```
鐢ㄦ埛锛?鐪嬬湅skill浼樺寲鍘嗗彶"
鈫?璇诲彇骞跺睍绀?results.tsv
```

---

## 璁捐鐏垫劅

> "You write the goals and constraints in program.md; let an agent generate and test code deltas indefinitely; keep only what measurably improves the objective."
> 鈥?Karpathy, autoresearch

鏈瑂kill鐨勫搴斿叧绯伙細
- **program.md** 鈫?鏈枃浠讹紙璇勪及rubric鍜岀害鏉熻鍒欙級
- **train.py** 鈫?姣忎釜SKILL.md
- **val_bpb** 鈫?9缁村姞鏉冩€诲垎锛堝惈瀹炴祴琛ㄧ幇 + meta-skill 鍙嶄緥榛戝悕鍗曪級
- **git ratchet** 鈫?鍙繚鐣欐湁鏀硅繘鐨刢ommit
- **test set** 鈫?姣忎釜skill鐨則est-prompts.json

鍖哄埆锛氬鍔犱簡浜哄湪鍥炶矾锛坅utoresearch鏄叏鑷富鐨勶紝skill浼樺寲闇€瑕佷汉鐨勫垽鏂姏锛夛紝浠ュ強鍙岄噸璇勪及鏈哄埗锛堢粨鏋?鏁堟灉锛夛紝鍥犱负skill鐨勩€屽ソ鍧忋€嶆瘮loss鏁板€兼洿寰銆?
### 瀛︽湳渚濇嵁 & Credits

- **SkillLens**锛坅rXiv [2605.23899](https://arxiv.org/abs/2605.23899)锛夛細9 缁?rubric 鐨勫疄璇佹潵婧愶紙LLM 鑷瘎 46.4% 鈫?鍔?meta-skill 涓夌淮搴﹀悗 73.8%锛夈€?- **SkillOpt**锛坅rXiv [2605.23904](https://arxiv.org/abs/2605.23904)锛夛細validation-gated edits 褰㈠紡鍖栨鏋躲€備唬鐮?[github.com/microsoft/SkillOpt](https://github.com/microsoft/SkillOpt)锛坄pip install skillopt`锛夈€侀」鐩〉 [microsoft.github.io/SkillOpt](https://microsoft.github.io/SkillOpt/)銆傪煠?2026-06-03 寰蒋瀹樻柟浠撳簱宸叉妸 darwin-skill 鍒楀叆闆嗘垚鍚嶅崟銆?- **autoresearch**锛歔github.com/karpathy/autoresearch](https://github.com/karpathy/autoresearch)锛屾湰 skill 1.0 鐨勫師濮嬬伒鎰熴€?
---

## 鎴愭灉鍗＄墖鐢熸垚锛圧esult Card锛?
姣忎釜skill浼樺寲瀹屾垚鍚庯紙鎴栧叏閲忔眹鎬诲悗锛夛紝鑷姩鐢熸垚瑙嗚鎴愭灉鍗＄墖锛屾埅鍥句繚瀛樹负PNG銆?
### 鍗＄墖妯℃澘

妯℃澘浣嶇疆锛歚templates/result-card.html`

3绉嶉鏍硷紝姣忔闅忔満閫夋嫨涓€绉嶏細

| 椋庢牸 | CSS绫?| URL hash | 瑙嗚鐗圭偣 |
|------|--------|----------|---------|
| Warm Swiss | `.theme-swiss` | `#swiss` | 鏆栫櫧搴?璧ら櫠姗欙紝Inter瀛椾綋锛屽共鍑€缃戞牸 |
| Dark Terminal | `.theme-terminal` | `#terminal` | 杩戦粦搴?鑽у厜缁匡紝绛夊瀛椾綋锛屾壂鎻忕嚎 |
| Newspaper | `.theme-newspaper` | `#newspaper` | 鏆栫櫧绾?娣辩孩锛岃‖绾垮瓧浣擄紝鍙屾爮缂栬緫椋?|

### 鐢熸垚娴佺▼

```
1. 澶嶅埗 templates/result-card.html 鍒颁复鏃跺伐浣滄枃浠?2. 鐢?sed/缂栬緫宸ュ叿 鏇挎崲鍗犱綅鏁版嵁锛?   - data-field="skill-name" 鈫?瀹為檯skill鍚?   - data-field="score-before/after/delta" 鈫?瀹為檯鍒嗘暟
   - 9涓淮搴︾殑 dim-bar-before/after width 鈫?瀹為檯鐧惧垎姣旓紙鑻ユā鏉夸粛鏄棫 8 缁村竷灞€锛屽姞涓€琛?dim9 鍙嶄緥榛戝悕鍗曟潯鐩級
   - data-field="improvement-1/2/3" 鈫?瀹為檯鏀硅繘鎽樿
   - data-field="date" 鈫?褰撳墠鏃ユ湡
3. 闅忔満閫夋嫨椋庢牸锛歨ash 璁句负 swiss/terminal/newspaper 涔嬩竴
4. 鐢?scripts/screenshot.mjs 鎴浘锛?x 楂樻竻锛屽彧鎴?.card 鍏冪礌锛岃嚜鍔?open 鍥剧墖锛夛細
   node .claude/skills/darwin-skill/scripts/screenshot.mjs \
     /abs/path/to/card.html /abs/path/to/output.png
   # 鍥為€€鏂规锛堣剼鏈け璐ユ椂锛夛細
   npx playwright screenshot "file:///path/to/card.html#[theme]" \
     output.png --viewport-size=960,1280 --wait-for-timeout=2000
5. 鎻愮ず鐢ㄦ埛鏌ョ湅鎴愭灉鍗＄墖 PNG

### 璧勬簮鏂囦欢閫熸煡

| 璺緞 | 鐢ㄩ€?|
|---|---|
| `templates/result-card.html` | 3椋庢牸涓绘ā鏉匡紙swiss/terminal/newspaper锛宧ash鍒囨崲锛?|
| `templates/result-card-dark.html` / `-white.html` | 鍗曚竴椋庢牸鏇夸唬妯℃澘锛堥渶瑕侀攣瀹氶鏍兼椂鐢級 |
| `scripts/screenshot.mjs` | 2x 楂樻竻鎴浘锛屽彧鎴?.card锛岃嚜鍔?open |
| `results.tsv` | 鍘嗘浼樺寲鏃ュ織锛?鍒楀惈 eval_mode锛?|
| `{skill鐩綍}/test-prompts.json` | 姣忎釜 skill 鐨勬祴璇?prompt 闆嗭紙鐢ㄤ簬缁村害8瀹炴祴锛?|

### 浣曟椂鐢熸垚

- **鍗晄kill鍗＄墖**锛氭瘡涓猻kill浼樺寲瀹屾垚鍚庯紝灞曠ず璇kill鐨勫垎鏁板彉鍖?- **鎬昏鍗＄墖**锛氬叏閮ㄤ紭鍖栧畬鎴愬悗锛圥hase 3锛夛紝灞曠ず鍏ㄥ眬鎴樼哗

### 鍝佺墝鍏冪礌

- 椤堕儴锛欴arwin.skill 鍝佺墝鏍囪瘑 + 鏃ユ湡
- 搴曢儴锛氥€孴rain your Skills like you train your models銆? github.com/alchaincyf/darwin-skill
