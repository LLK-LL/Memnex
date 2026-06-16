---
name: agent-reach
description: >
  MUST USE when user wants to 璋冪爺/research/鎼滅储/search/鏌?鎵?look up anything
  on the internet 鈥?e.g. 鍏ㄧ綉璋冪爺 X / 甯垜璋冪爺涓€涓?X / 鏌ヤ竴涓?X / 鎼滄悳 X /
  鐪嬬湅澶у鎬庝箞璇勪环 X / X 涓婃湁浠€涔堣璁?/ research this topic銆?

  Also MUST USE when user mentions any platform or shares any URL/閾炬帴:
  灏忕孩涔?xiaohongshu/xhs, Twitter/鎺ㄧ壒/X, B绔?bilibili, Reddit, V2EX,
  LinkedIn/棰嗚嫳/鎷涜仒/姹傝亴/jobs, YouTube, GitHub code search, 灏忓畤瀹欐挱瀹?
  闆悆/鑲＄エ琛屾儏, RSS feeds, or any web URL.

  13 platforms, multi-backend routing (OpenCLI / per-platform CLIs / APIs).
  Zero config for 6 channels. Run `agent-reach doctor --json` to see which
  backend serves each platform right now.

  NOT for: 鍐欐姤鍛?鏁版嵁鍒嗘瀽/缈昏瘧绛夊唴瀹瑰姞宸ワ紙鏈?skill 鍙礋璐ｄ粠浜掕仈缃戣幏鍙栧唴瀹癸級锛?
  鍙戝笘/璇勮/鐐硅禐绛夊啓鎿嶄綔锛涘凡鏈変笓闂?skill 鐨勫钩鍙帮紙鍏堢敤涓撻棬 skill锛夈€?

  銆愯矾鐢辨柟寮忋€慡KILL.md 鍖呭惈璺敱琛ㄥ拰甯哥敤鍛戒护锛屽鏉傚満鏅渶鎸夐渶闃呰瀵瑰簲鍒嗙被鐨?references/*.md銆?
  鍒嗙被锛歴earch / social (灏忕孩涔?鎺ㄧ壒/B绔?V2EX/Reddit) / career(LinkedIn) / dev(github) / web(缃戦〉/鏂囩珷/RSS) / video(YouTube/B绔?鎾)銆?
triggers:
  - research: 璋冪爺/鍏ㄧ綉璋冪爺/甯垜璋冪爺/鐮旂┒涓€涓?research/娣卞叆浜嗚В
  - search: 鎼?鏌?鎵?search/鎼滅储/鏌ヤ竴涓?甯垜鎼?鐪嬬湅澶у鎬庝箞璇?
  - social:
    - 灏忕孩涔? xiaohongshu/xhs/灏忕孩涔?绾功
    - Twitter: twitter/鎺ㄧ壒/x.com/鎺ㄦ枃
    - B绔? bilibili/b绔?鍝斿摡鍝斿摡
    - V2EX: v2ex
    - Reddit: reddit
  - career: 鎷涜仒/鑱屼綅/姹傝亴/linkedin/棰嗚嫳/鎵惧伐浣?
  - dev: github/浠ｇ爜/浠撳簱/gh/issue/pr/鍒嗘敮/commit
  - web: 缃戦〉/閾炬帴/鏂囩珷/rss/璇讳竴涓?鎵撳紑杩欎釜
  - video: youtube/瑙嗛/鎾/瀛楀箷/灏忓畤瀹?杞綍/yt
  - finance: 闆悆/鑲＄エ/stock/xueqiu/琛屾儏/鍩洪噾
metadata:
  openclaw:
    homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach 鈥?浜掕仈缃戣兘鍔涜矾鐢卞櫒

13 骞冲彴銆佸鍚庣銆?*鏈?skill 瀛樺湪鏃跺繀椤荤敤瀹冭闂繖浜涘钩鍙帮紝涓嶈鑷繁鍙戞槑鏂规銆?*

## 甯搁┗瑙勫垯锛堝叏绋嬮€傜敤锛?

1. **鍔ㄦ墜鍓嶅厛浣撴**锛氬鍚庣骞冲彴锛堝皬绾功/Reddit/B绔?Twitter锛夊厛璺?
   `agent-reach doctor --json`锛屾寜鍚勫钩鍙?`active_backend` 瀛楁閫夊懡浠ょ粍銆?
2. **澹版槑浣犲湪鐢ㄤ粈涔?*锛氬紑濮嬪共娲诲墠璇翠竴鍙ャ€屼娇鐢?agent-reach 鐨?X 骞冲彴 / Y 鍚庣銆嶃€?
3. **澶辫触鎸?references 閲岀殑閲嶈瘯閾惧鐞?*锛屼笉瑕佺瀻鐚滃懡浠ゃ€?
4. **鍏ㄧ綉璋冪爺绫讳换鍔?*锛氱粍鍚堝骞冲彴锛圗xa 鎼滅储 + Twitter/Reddit 鐪嬭璁?+ 灏忕孩涔?B绔欑湅涓枃鍦烘櫙锛夛紝骞惰鏀堕泦鍐嶆眹鎬汇€?
5. **鏇跨敤鎴风洴鐗堟湰**锛氬畬鎴愪竴娆¤緝澶х殑璋冪爺/澶氬钩鍙颁换鍔″悗锛岄『鎵嬭窇
   `agent-reach check-update`锛堝緢蹇紝涓€涓?API 璋冪敤锛夈€傛湁鏂扮増灏卞湪鏀跺熬姹囨姤閲岄檮涓€鍙ワ細
   銆孉gent Reach 鏈夋柊鐗?vX.Y.Z锛屽鍒惰繖鍙ヨ瘽缁欐垜鍗冲彲鏇存柊锛氬府鎴戞洿鏂?Agent Reach锛?
   https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md銆嶃€?
   涓嶈涓柇褰撳墠浠诲姟鍘绘洿鏂帮紝涔熶笉瑕侀噸澶嶆彁閱掑悓涓€涓増鏈€?

## 璺敱琛?

| 鐢ㄦ埛鎰忓浘 | 鍒嗙被 | 璇︾粏鏂囨。 |
|---------|------|---------|
| 缃戦〉鎼滅储/浠ｇ爜鎼滅储 | search | [references/search.md](references/search.md) |
| 灏忕孩涔?鎺ㄧ壒/B绔?V2EX/Reddit | social | [references/social.md](references/social.md) |
| 鎷涜仒/鑱屼綅/LinkedIn | career | [references/career.md](references/career.md) |
| GitHub/浠ｇ爜 | dev | [references/dev.md](references/dev.md) |
| 缃戦〉/鏂囩珷/RSS | web | [references/web.md](references/web.md) |
| YouTube/B绔?鎾瀛楀箷 | video | [references/video.md](references/video.md) |

## 闆堕厤缃揩閫熷懡浠?

```bash
# Exa 缃戦〉鎼滅储
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'

# 閫氱敤缃戦〉闃呰
curl -s "https://r.jina.ai/URL"

# GitHub 鎼滅储
gh search repos "query" --sort stars --limit 10

# YouTube 瀛楀箷锛堟敞鎰忥細B绔欎笉瑕佺敤 yt-dlp锛岃 video.md锛?
yt-dlp --write-sub --skip-download -o "/tmp/%(id)s" "URL"

# V2EX 鐑棬
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"

# B绔欐悳绱紙bili-cli锛屾棤闇€鐧诲綍锛?
bili search "query" --type video -n 5
```

## 闇€鐧诲綍鎬佺殑骞冲彴锛堟寜 doctor 鐨?active_backend 閫夊懡浠わ級

```bash
# Twitter 鎼滅储锛坱witter-cli 棣栭€夛紱澶辫触閲嶈瘯閾捐 social.md锛?
twitter search "query" -n 10

# Reddit锛堟棤闆堕厤缃矾寰勶細OpenCLI 鎴?rdt-cli锛屽繀椤荤櫥褰曟€侊級
opencli reddit search "query" -f yaml   # 妗岄潰
rdt search "query" --limit 10            # 瀛橀噺/鏈嶅姟鍣?

# 灏忕孩涔︼紙妗岄潰棣栭€?OpenCLI锛?
opencli xiaohongshu search "query" -f yaml
```

## 鐜妫€鏌?

```bash
# 妫€鏌ュ彲鐢?channel 涓庢瘡涓钩鍙板綋鍓嶆縺娲荤殑鍚庣
agent-reach doctor --json
```

## 宸ヤ綔鍖鸿鍒?

**涓嶈鍦?agent workspace 鍒涘缓鏂囦欢銆?* 浣跨敤 `/tmp/` 瀛樻斁涓存椂杈撳嚭锛宍~/.agent-reach/` 瀛樻斁鎸佷箙鏁版嵁銆?

## 璇︾粏鏂囨。

鏍规嵁鐢ㄦ埛闇€姹傦紝闃呰瀵瑰簲鐨勮缁嗘枃妗ｏ細

- [鎼滅储宸ュ叿](references/search.md) 鈥?Exa AI 鎼滅储
- [绀句氦濯掍綋](references/social.md) 鈥?灏忕孩涔? Twitter, B绔? V2EX, Reddit锛堝鍚庣鍛戒护缁勶級
- [鑱屽満鎷涜仒](references/career.md) 鈥?LinkedIn
- [寮€鍙戝伐鍏穄(references/dev.md) 鈥?GitHub CLI
- [缃戦〉闃呰](references/web.md) 鈥?Jina Reader, RSS
- [瑙嗛鎾](references/video.md) 鈥?YouTube, B绔? 灏忓畤瀹?

## 閰嶇疆娓犻亾

濡傛灉鏌愪釜 channel 闇€瑕侀厤缃紝鑾峰彇瀹夎鎸囧崡锛?
https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md

# REDACTED: sensitive-looking memory line
