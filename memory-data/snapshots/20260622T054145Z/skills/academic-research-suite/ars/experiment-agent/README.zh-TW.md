# 瀵﹂浠ｇ悊浜?(Experiment Agent)

[![Version](https://img.shields.io/badge/version-1.0-blue)](https://github.com/Imbad0202/experiment-agent/releases)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Sponsor](https://img.shields.io/badge/sponsor-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/crucify020v)

Claude Code 鎶€鑳斤細鍩疯銆佺洠鎺с€佽В璁€銆侀璀夊琛撶爺绌跺椹椼€?

## 鍔熻兘

- **鍩疯绋嬪紡纰煎椹?* 鈥?鍩疯鑵虫湰锛圥ython銆丷 绛夛級锛屽嵆鏅傜洠鎺?stall/crash锛屾敹闆嗙祼鏋?
- **绠＄悊浜哄伐鐮旂┒** 鈥?瑕忓妰 protocol銆佹鏌?IRB 鍊悊銆佽拷韫よ硣鏂欐敹闆嗛€插害
- **绲辫▓瑙ｈ畝** 鈥?瑙ｈ畝 p-value銆佹晥鏋滈噺銆佷俊璩村崁闁擄紱妾㈡煡 11 绋当瑷堣瑾わ紙Simpson's Paradox銆佸瓨娲昏€呭亸瑾ょ瓑锛?
- **椹楄瓑閲嶇従鎬?* 鈥?閲嶆柊鍩疯瀵﹂涓︽瘮灏嶇祼鏋?

## 鐐轰粈楹奸渶瑕?

Lu et al.锛?026, *Nature*锛夊睍绀轰簡鑷富 AI 鐮旂┒鐨勫椹楅€插害绠＄悊鍣ㄣ€傛湰鎶€鑳藉皣鍚屾ǎ鐨勫煼琛岃垏鐩ｆ帶鑳藉姏甯跺叆浜洪鍙冭垏鐨勫琛撳伐浣滄祦绋嬧€斺€斾笉鎵挎摂鍏ㄨ嚜鍕曞寲鐨勯ⅷ闅€?

## 妯″紡

| 妯″紡 | 鍔熻兘 |
|------|------|
| `run` | 鍩疯绋嬪紡纰?+ 鐩ｆ帶 process |
| `manage` | 瑕忓妰 + 杩借工浜哄伐鐮旂┒ |
| `validate` | 绲辫▓瑙ｈ畝 + 閲嶇従鎬ч璀?|
| `plan` | Socratic 灏嶈┍瑷▓瀵﹂ |

## 蹇€熼枊濮?

1. Clone 鏈?repo 鍒颁綘鐨勫皥妗堟垨 `.claude/skills/`
# REDACTED: sensitive-looking memory line
3. 瑭﹁│锛氥€岃窇鎴戠殑鍒嗘瀽锛歚Rscript analysis.R`銆?

## ARS 鐩稿鎬?

鏈妧鑳藉彲鐛ㄧ珛浣跨敤锛屼篃鍙伕鎿囨€ф暣鍚?[Academic Research Skills (ARS)](https://github.com/Imbad0202/academic-research-skills)锛?

- 璁€鍙?ARS Stage 1 杓稿嚭锛圧Q Brief銆丮ethodology Blueprint锛夐爯濉椹楄ō瑷?
- 鐢㈠嚭绗﹀悎 Material Passport銆佷笖鏄庣⒑妯欑ず verification status 鐨勮几鍑轰緵 ARS Stage 2 浣跨敤
- ARS 涓嶉渶瑕佷换浣曚慨鏀光€斺€斾娇鐢ㄨ€呮墜鍕曢姕鎺?

### 浣曟檪鎼厤 ARS 浣跨敤

鍦?ARS pipeline 涓紝experiment-agent 浠嬫柤 **Stage 1锛堢爺绌讹級鍜?Stage 2锛堝浣滐級涔嬮枔**锛?

```
ARS Stage 1 鐮旂┒      鈫? 鍙栧緱 RQ Brief + Methodology Blueprint
        鈫?
  [鏆仠 ARS pipeline]
        鈫?
  experiment-agent     鈫? plan 鈫?run/manage 鈫?validate 鈫?鍙栧緱鍒嗘瀽鎴栭璀夐亷鐨勭祼鏋?
        鈫?
  [绻肩簩 ARS pipeline]
        鈫?
ARS Stage 2 瀵綔      鈫? 鐢ㄥ椹楃祼鏋滄挵瀵珫鏂?
```

鐣朵綘鐨勭爺绌堕渶瑕佽窇瀵﹂锛堢▼寮忕⒓鎴栦汉宸ョ爺绌讹級鎵嶈兘闁嬪瀵綔鏅傦紝浣跨敤 experiment-agent銆傚鏋滆珫鏂囩磾绮瑰熀鏂兼枃鐛诲洖椤ф垨浜屾璩囨枡鍒嗘瀽锛屼笉闇€瑕侀€欏€嬪伐鍏凤紝鐩存帴寰?ARS Stage 1 閫插叆 Stage 2銆?

### 濡備綍杓夊叆

**姝ラ 1**锛欳lone 鏈?repo 鍒?ARS 灏堟鏃侊紙鎴栦换浣曚綅缃級锛?

```bash
cd ~/Projects/HEEACT
git clone https://github.com/Imbad0202/experiment-agent.git
```

# REDACTED: sensitive-looking memory line

```bash
cd ~/Projects/HEEACT/experiment-agent
claude
```

# REDACTED: sensitive-looking memory line

# REDACTED: sensitive-looking memory line

> 涔熷彲浠ラ€忛亷 `.claude/skills/` symlink 灏囨湰鎶€鑳藉姞鍏ヤ换浣曞皥妗堛€?

## 瀹夊叏姗熷埗

- 鍙煼琛屼綘鎸囧畾鐨勫懡浠も€斺€斿緸涓嶈嚜鍕曠敓鎴愭垨淇敼浣犵殑绋嬪紡纰?
- 寰炰笉鑷嫊閲嶈│ crash 鐨勫椹?
- 寰炰笉鎺ヨЦ鍘熷鍙冭垏鑰呰硣鏂?
- 绲辫▓瑙ｈ畝鏄弿杩版€х殑锛屼笉浠ｆ浛浣犱笅绲愯珫
- 瀹屾暣娓呭柈瑕?SKILL.md 瀹夊叏瑕忓墖

## 鎺堟瑠

CC-BY-NC 4.0

## 浣滆€?

鍚虫壙缈?(Cheng-I Wu)

---

## 璁婃洿绱€閷?

瑕?[CHANGELOG.md](CHANGELOG.md)
