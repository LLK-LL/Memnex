# 绀句氦濯掍綋 & 绀惧尯

灏忕孩涔︺€乀witter/X銆丅绔欍€乂2EX銆丷eddit銆?

## 灏忕孩涔?/ XiaoHongShu锛堝鍚庣锛?

灏忕孩涔︽湁涓変釜鍚庣锛?*鍏堣窇 `agent-reach doctor --json` 鐪?xiaohongshu 鐨?`active_backend` 鏄摢涓?*锛屽啀鐢ㄥ搴斿懡浠ょ粍銆?

### 鍚庣 A锛歄penCLI锛堟闈㈤閫夛紝澶嶇敤娴忚鍣ㄧ櫥褰曟€侊級

```bash
# 鎼滅储绗旇
opencli xiaohongshu search "query" -f yaml

# REDACTED: sensitive-looking memory line
opencli xiaohongshu note "NOTE_URL" -f yaml

# 璇勮锛堟敮鎸佹ゼ涓ゼ锛?
opencli xiaohongshu comments NOTE_ID -f yaml

# 棣栭〉鎺ㄨ崘 feed
opencli xiaohongshu feed -f yaml

# 鐢ㄦ埛涓婚〉鍏紑绗旇
opencli xiaohongshu user USER_ID -f yaml
```

# REDACTED: sensitive-looking memory line

### 鍚庣 B锛歺iaohongshu-mcp锛堟湇鍔″櫒鍦烘櫙锛?

```bash
# 鏈櫥褰曟椂锛氬厛鏌ョ姸鎬侊紝鍐嶅彇浜岀淮鐮佺粰鐢ㄦ埛鎵?
mcporter call 'xiaohongshu.check_login_status()' --timeout 120000
mcporter call 'xiaohongshu.get_login_qrcode()' --timeout 120000

# 鎼滅储
mcporter call 'xiaohongshu.search_feeds(keyword: "query")' --timeout 120000

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
```

> 棣栨璋冪敤浼氳嚜鍔ㄤ笅杞界害 150MB 鏃犲ご娴忚鍣紝鍔″繀甯?`--timeout 120000`銆傛湭鐧诲綍鏃?search 浼氭寕姝伙紝鍏?check_login_status銆?

### 鍚庣 C锛歺hs-cli锛堝瓨閲忓閫夛紝涓婃父 2026-03 璧峰仠鏇达級

```bash
xhs search "query"          # 鎼滅储
xhs read NOTE_ID_OR_URL     # 璇荤瑪璁帮紙蹇呴』鐢ㄦ悳绱㈢粨鏋滀腑鐨?URL/ID锛屼笉鑳借８ note_id锛?
xhs comments NOTE_ID_OR_URL # 璇勮
xhs hot                     # 鐑棬
xhs feed                    # 鎺ㄨ崘
```

> 宸茬煡涓嶇ǔ瀹氾細`xhs user` / `xhs user-posts` / `xhs favorites` 鍙兘杩斿洖 API error锛堜笂娓稿仠鏇存棤浜轰慨锛夈€傛柊瑁呯敤鎴峰缓璁洿鎺ヨ蛋鍚庣 A/B銆?

### 閫氱敤娉ㄦ剰浜嬮」

# REDACTED: sensitive-looking memory line
>
> **棰戠巼鎺у埗**: 楂橀璇锋眰锛堟壒閲忔悳绱€佹繁缈昏瘎璁猴級浼氳Е鍙戦獙璇佺爜锛屽钩鍙伴檺鍒舵棤娉曠粫杩囥€傛瘡娆℃搷浣滈棿闅?2-3 绉掋€?
>
> **鍐欐搷浣滐紙鍙戝笘/璇勮/鐐硅禐锛?*: 寤鸿鍙銆倄hs-cli v0.6.x 鍐欐搷浣滃彲鑳藉洜绛惧悕闂杩斿洖 406銆?

## Twitter/X (twitter-cli)

### 绋冲畾鍛戒护

```bash
# 棣栭〉鏃堕棿绾匡紙鏈€绋冲畾锛?
twitter feed -n 20

# 璇诲彇鍗曟潯鎺ㄦ枃锛堝惈鍥炲锛?
twitter tweet URL_OR_ID

# 璇诲彇闀挎枃 / X Article
twitter article URL_OR_ID

# 鐢ㄦ埛鏃堕棿绾?
twitter user-posts @username -n 20

# 鐢ㄦ埛璧勬枡
twitter user @username
```

### 鍙兘涓嶇ǔ瀹氱殑鍛戒护

```bash
# 鎼滅储鎺ㄦ枃锛圱witter 棰戠箒鏀?GraphQL 绔偣锛屽彲鑳?404锛?
twitter search "query" -n 10

# likes锛?024 骞村悗鍙兘鐪嬭嚜宸辩殑锛屽钩鍙伴檺鍒讹級
twitter likes
```

### search 澶辫触鏃剁殑閲嶈瘯閾撅紙鎸夊簭鎵ц锛屾垚鍔熷嵆鍋滐級

1. 鐩存帴閲嶈瘯涓€娆★紙鍋跺彂澶辫触甯歌锛夛細`twitter search "query" -n 10`
2. 鍗囩骇鍚庡啀璇曪細`pipx upgrade twitter-cli && twitter search "query" -n 10`
3. 鎹?OpenCLI 澶囬€夛紙妗岄潰锛屽鐢ㄦ祻瑙堝櫒鐧诲綍鎬侊級锛歚opencli twitter search "query" -f yaml`
4. 閮戒笉琛屽氨鏀圭敤 `twitter feed` / `twitter user-posts @somebody` 绛夌ǔ瀹氬懡浠ょ粫璺?

### 閲嶈娉ㄦ剰浜嬮」

> **瀹夎**: `pipx install twitter-cli`锛堢‘淇?v0.8.5+锛?
>
# REDACTED: sensitive-looking memory line
>
> **IP 椋庢帶**: 涓嶈鍦?VPS/鏁版嵁涓績 IP 涓婇绻佽皟鐢紝灏ゅ叾鏄?followers/following锛屾湁灏佸彿椋庨櫓銆備娇鐢ㄤ綇瀹呬唬鐞嗘垨鏈湴鐜銆?
>
# REDACTED: sensitive-looking memory line
>
> **杈撳嚭鏍煎紡**: 寤鸿鐢?`--yaml` 鎴?`--json` 鑾峰緱缁撴瀯鍖栬緭鍑猴紝瀵?AI agent 鏇村弸濂姐€?

## B绔?/ Bilibili

> 鈿狅笍 **涓嶈鐢?yt-dlp 璇?B绔?*锛堥鎺у凡鍏ㄩ潰 412 鎷︽埅锛屽疄娴嬫棤瑙ｏ級銆傜敤 bili-cli / OpenCLI銆?

```bash
# 鎼滅储 / 鐑棬 / 瑙嗛璇︽儏锛坆ili-cli锛屽彧璇绘棤闇€鐧诲綍锛?
bili search "query" --type video -n 5
bili hot -n 10
bili video BVxxx

# 瀛楀箷锛圤penCLI锛岄渶妗岄潰 Chrome锛?
opencli bilibili subtitle BVxxx
```

> 璇︾粏鍛戒护锛堥煶棰戣浆鍐欍€丄PI 鐩磋繛鍏滃簳锛夎 [references/video.md](video.md)銆?

## V2EX (鍏紑 API)

鏃犻渶璁よ瘉锛岀洿鎺ヨ皟鐢ㄥ叕寮€ API銆?

### 鐑棬涓婚

```bash
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"
```

### 鑺傜偣涓婚

```bash
# node_name 濡? python, tech, jobs, qna, programmers
curl -s "https://www.v2ex.com/api/topics/show.json?node_name=python&page=1" -H "User-Agent: agent-reach/1.0"
```

### 涓婚璇︽儏

```bash
# topic_id 浠?URL 鑾峰彇锛屽 https://www.v2ex.com/t/1234567
curl -s "https://www.v2ex.com/api/topics/show.json?id=TOPIC_ID" -H "User-Agent: agent-reach/1.0"
```

### 涓婚鍥炲

```bash
curl -s "https://www.v2ex.com/api/replies/show.json?topic_id=TOPIC_ID&page=1" -H "User-Agent: agent-reach/1.0"
```

### 鐢ㄦ埛淇℃伅

```bash
curl -s "https://www.v2ex.com/api/members/show.json?username=USERNAME" -H "User-Agent: agent-reach/1.0"
```

### Python 璋冪敤绀轰緥

```python
from agent_reach.channels.v2ex import V2EXChannel

ch = V2EXChannel()

# 鑾峰彇鐑棬甯栧瓙
topics = ch.get_hot_topics(limit=10)
for t in topics:
    print(f"[{t['node_title']}] {t['title']} ({t['replies']} 鍥炲)")

# 鑾峰彇鑺傜偣甯栧瓙
node_topics = ch.get_node_topics("python", limit=5)

# 鑾峰彇甯栧瓙璇︽儏 + 鍥炲
topic = ch.get_topic(1234567)
# REDACTED: sensitive-looking memory line

# 鑾峰彇鐢ㄦ埛淇℃伅
user = ch.get_user("Livid")
```

> **鑺傜偣鍒楄〃**: https://www.v2ex.com/planes

## Reddit锛堝鍚庣锛屽繀椤荤櫥褰曟€侊級

**Reddit 娌℃湁闆堕厤缃矾寰?*锛氬尶鍚?`.json` 绔偣宸茶灏侊紙403锛夛紝瀹樻柟 API 鑷?2025-11 璧蜂汉宸ュ鎵瑰熀鏈笉鎵广€備袱涓悗绔兘闈犵櫥褰曟€侊紝鍏堣窇 `agent-reach doctor --json` 鐪?reddit 鐨?`active_backend`銆備腑鍥藉ぇ闄嗚闂渶浠ｇ悊銆?

### 鍚庣 A锛歄penCLI锛堟闈㈤閫夛紝澶嶇敤娴忚鍣ㄧ櫥褰曟€侊級

```bash
# 鎼滅储甯栧瓙
opencli reddit search "query" -f yaml

# 璇诲笘瀛愬叏鏂?+ 璇勮
opencli reddit read POST_ID -f yaml

# 娴忚 subreddit / 鐑棬 / Popular
opencli reddit subreddit LocalLLaMA -f yaml
opencli reddit hot -f yaml
opencli reddit popular -f yaml

# subreddit 鍏冧俊鎭紙璁㈤槄鏁般€佺畝浠嬶級
opencli reddit subreddit-info LocalLLaMA -f yaml
```

> 瑕佹眰 Chrome 鎵撳紑涓旀祻瑙堝櫒閲岀櫥褰曡繃 reddit.com銆?

### 鍚庣 B锛歳dt-cli锛堝瓨閲?鏈嶅姟鍣ㄥ閫夛紝涓婃父 2026-03 璧峰仠鏇达級

```bash
rdt search "query" --limit 10   # 鎼滅储甯栧瓙
rdt read POST_ID                # 璇诲笘瀛愬叏鏂?+ 璇勮
rdt sub python --limit 20       # 娴忚 subreddit
rdt popular --limit 10          # 娴忚鐑棬
rdt all --limit 10              # 娴忚 /r/all
```

# REDACTED: sensitive-looking memory line
> 寤鸿浣跨敤 `--yaml` 杈撳嚭锛屽 AI agent 鏇村弸濂姐€?

### 楂樼骇閫夐」锛氬畼鏂?API + PRAW锛堜粎闄愬凡鏈夊嚟璇佺殑鐢ㄦ埛锛?

# REDACTED: sensitive-looking memory line
