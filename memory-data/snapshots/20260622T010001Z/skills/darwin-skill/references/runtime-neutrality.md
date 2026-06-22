# Runtime 閫傞厤鎬у鏌ワ紙璇︾粏瀵圭収琛?+ 鎵弿鍛戒护锛?
> SKILL.md 鍦ㄣ€孯untime 閫傞厤鎬у鏌ャ€嶇珷鑺備細寮曠敤鏈枃浠躲€侾hase 1 鍩虹嚎璇勪及鏃惰窇绾㈢伅鎵弿闇€瑕佹煡杩欓噷銆?
---

## 鑳屾櫙

鑺卞彅鐨?skills 鍩轰簬 Anthropic 寮€鏀剧殑 [Agent Skills](https://agentskills.io) 鍗忚锛屽簲褰撹兘鍦?Claude Code銆丆odex銆丆ursor銆丱penClaw銆丠ermes Agent銆丆odeBuddy銆乄orkbuddy銆丟emini CLI銆丱penCode 绛?50+ skills-compatible runtime 涓婇€氱敤銆?
杩欐槸 skill 鍒嗗彂鍔涚殑鏍规湰鈥斺€斾竴涓璇垽涓恒€屽崟涓€ runtime 缁戝畾銆嶇殑 skill锛屼細琚叾浠?agent 鐩存帴鎷掔粷瀹夎锛堝疄渚嬶細nuwa-skill 鍥?README 鍐欍€屽湪 Claude Code 閲屼娇鐢ㄣ€嶈 Marvis agent 鎷掔粷锛夈€?
**閫傜敤鑼冨洿**锛氶櫎闈?skill 鍚嶅瓧鏄庣‘澹版槑缁戝畾鍗曚竴 runtime锛堝 `huashu-slides-codex`銆乣xxx-for-claude-code`锛夛紝鎵€鏈?skill 蹇呴』閫氳繃鏈鏌ャ€?
---

## 绾㈢伅淇″彿锛堝嚭鐜板嵆鎵ｅ垎锛屽繀椤诲湪 P0 浼樺寲杞慨澶嶏級

| 绾㈢伅绫诲瀷 | 鍏稿瀷琛ㄧ幇 | 鍗卞 |
|---|---|---|
| Badge 閽夋 | `[![Claude Code Skill]]`銆乣[![Cursor Only]]` 涔嬬被鐨勫崟涓€ runtime badge | 瑙嗚涓婇灞忓畾璋冿紝鍏朵粬 runtime 鐢ㄦ埛鐩存帴閫€鍑?|
| 鎺緸閽夋 | 銆屽湪 Claude Code 閲屻€嶃€孋ursor 鐢ㄦ埛鍙互銆嶃€孋odex 涓娇鐢ㄣ€嶃€孋laude Code skill銆?| 璁?agent 瑙ｆ瀽鏃惰鍒や负"涓嶆槸缁欐垜鐢ㄧ殑" |
| 瀹夎鍛戒护閽夋 | 鍙粰 `~/.claude/skills/` 璺緞銆佸彧缁?`/plugin install`銆佸彧缁欐煇 runtime 绉佹湁 CLI | 涓嶇煡閬撹繖鏄?Claude Code 鍛戒护鐨?agent 浼氭嫆缁?|
| 宸ュ叿璋冪敤閽夋 | 宸ヤ綔娴侀噷纭紪鐮?`mcp__claude-in-chrome__*`銆乣PostToolUse hook` 绛夊崟 runtime 鑳藉姏锛屼笖涓嶇粰鏇夸唬鏂规 | 鍏朵粬 runtime 娌¤繖浜涘伐鍏?鈫?娴佺▼璺戜笉閫?|
| 璺緞纭紪鐮?| `~/.claude/skills/xxx/`銆乣.claude/agents/yyy` 浣滀负鍞竴璺緞 | 鍏朵粬 runtime 鐢?`~/.cursor/skills/` `~/.codex/skills/` |

---

## 缁跨伅鎺緸锛堟帹鑽愭敼鍐欙級

| 绾㈢伅 | 缁跨伅 |
|---|---|
| "鍦?Claude Code 閲? | "鍦ㄤ綘鐨?agent 閲? / "鍦ㄤ换浣?skills-compatible runtime 涓? |
| "Claude Code skill" | "Agent Skill" |
| "Claude Code 鐢ㄦ埛" | "skills-aware agent 鐢ㄦ埛" |
| 鍗曚竴 badge 閽夋 | `Agent Skills Standard` + `skills.sh Compatible` + `Multi-Runtime` 涓変釜涓珛 badge |
| 鍙粰 `npx skills add ...` 涓€琛?| 涓夊眰缁撴瀯锛氣憼 鑷姩妫€娴嬬殑涓€琛屽懡浠?鈶?鎶樺彔灞曞紑鐨勫悇 runtime 鎵嬪姩璺緞 鈶?銆屼綔涓哄弬鑰冭祫鏂?cat 杩?context銆峟allback |
| 宸ュ叿鍚嶇‖缂栫爜 | "鐢ㄤ竴涓?browser automation 宸ュ叿锛堜緥濡?Claude 鐨?chrome MCP銆丳laywright 绛夛級" |

---

## 渚嬪娓呭崟锛堝厑璁哥殑銆孋laude Code 鐥曡抗銆嶏級

涓嶆槸鎵€鏈?Claude-Code 鐩稿叧瀛楃閮借娓呴櫎銆備笅闈㈣繖浜涙槸**姝ｅ綋鍑虹幇**鐨勶紝涓嶇畻绾㈢伅锛?
1. **Frontmatter `description` 閲岀殑涓嫳鏂囪Е鍙戣瘝**鈥斺€旇繖鏄?skill 鍏ュ彛锛屽叾浠?runtime 瑙ｆ瀽 frontmatter 鏃跺悓鏍疯兘鍖归厤
2. **鑺卞彅鐢熸€佸唴閮ㄨ仈鍔ㄧ殑 skill 鍚嶅紩鐢?*鈥斺€斿銆岃皟鐢?huashu-design銆嶃€岃窡 darwin-skill 閰嶅銆?3. **鏄庣‘鏍囨敞鐨?runtime-specific 绔犺妭**鈥斺€斿銆?## 浠?Claude Code 浼樺寲锛堟寜闇€瑙﹀彂锛夈€? 瑙ｉ噴娓呮鏄?nice-to-have
4. **commit message銆乧hangelog銆佸唴閮ㄨ剼鏈?*鈥斺€斾笉灞炰簬鐢ㄦ埛璇诲埌鐨?skill 鍐呭

---

## 瀹℃煡鏃舵満

- **Phase 1 鍩虹嚎璇勪及鏃?*锛氭瘡涓?skill 璺戜竴娆＄孩鐏壂鎻忥紝鍛戒腑椤逛互 `runtime_warn=N` 褰㈠紡鍐欏叆 results.tsv 鐨?`note` 鍒楋紙涓嶆柊澧炲垪銆佷繚鎸佸悜鍚庡吋瀹癸級
- **Phase 2 浼樺寲寰幆鏃?*锛氱孩鐏懡涓暟 鈮?1 鐨?skill锛屽己鍒舵妸绗竴杞紭鍖栨柟鍚戝畾涓?P0銆宺untime drift 淇銆嶏紙璇﹁ SKILL.md 浼樺寲绛栫暐搴撶殑 P0 绔犺妭锛夛紝浼樺厛浜庡叾浠栫淮搴?- **Phase 3 姹囨€绘姤鍛婃椂**锛氬崟鐙竴鏍忋€宺untime 涓珛搴︺€嶅睍绀轰慨澶嶈繘搴︼紙鍛戒腑鏁颁粠 X 鈫?0锛?
---

## 绾㈢伅鎵弿蹇€熷懡浠?
```bash
# 鍦?skill 鐩綍璺戣繖涓?grep锛岃緭鍑哄嵆绾㈢伅鍛戒腑
grep -nE "(鍦?Claude Code|Claude Code skill|Claude Code 鐢ㄦ埛|Cursor only|Codex 涓瓅^\[!\[Claude Code|~/\.claude/skills/[a-z]|/plugin install\b)" SKILL.md README.md 2>/dev/null
```

杈撳嚭闈炵┖ = 璇?skill 鏈€氳繃 gate锛屽繀椤诲湪浼樺寲寰幆閲屼慨澶嶃€?
