# 瑙嗛/鎾

YouTube銆丅绔欍€佸皬瀹囧畽鎾鐨勫瓧骞曞拰杞綍銆?

## YouTube (yt-dlp)

### 鑾峰彇瑙嗛鍏冩暟鎹?

```bash
yt-dlp --dump-json "URL"
```

### 涓嬭浇瀛楀箷

```bash
# 涓嬭浇瀛楀箷 (涓嶄笅杞借棰?
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"

# 鐒跺悗璇诲彇 .vtt 鏂囦欢
cat /tmp/VIDEO_ID.*.vtt
```

### 鑾峰彇璇勮

```bash
# 鎻愬彇璇勮锛坆est-effort锛屼笉淇濊瘉瀹屾暣锛?
yt-dlp --write-comments --skip-download --write-info-json \
  --extractor-args "youtube:max_comments=20" \
  -o "/tmp/%(id)s" "URL"
# 璇勮鍦?.info.json 鐨?comments 瀛楁涓?
```

### 鎼滅储瑙嗛

```bash
yt-dlp --dump-json "ytsearch5:query"
```

> **瀛楀箷娉ㄦ剰**: 鎵嬪姩涓婁紶鐨勫瓧骞曟彁鍙栧彲闈狅紱鑷姩鐢熸垚瀛楀箷鍙兘瀛樺湪琛岄棿閲嶅锛岄渶鍚庡鐞嗐€?
> **璇勮娉ㄦ剰**: `--write-comments` 鍩轰簬缃戦〉鎶撳彇锛堥潪 YouTube Data API锛夛紝閮ㄥ垎璇勮鍙兘涓㈠け銆?

### 鏃犲瓧骞曞厹搴曪細Whisper 闊抽杞啓

```bash
# 瑙嗛娌℃湁瀛楀箷鏃剁殑鍏滃簳锛氫笅杞介煶棰戝苟鐢?Whisper 杞啓锛圙roq 鍏嶈垂 key 鍗冲彲锛?
agent-reach transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
agent-reach transcribe ./local_audio.mp3 -o /tmp/transcript.txt
```

> 闇€瑕佸厛閰嶇疆 key锛歚agent-reach configure groq-key gsk_xxx`锛堝厤璐癸紝console.groq.com锛?
> 鎴?`agent-reach configure openai-key sk-xxx`銆傞粯璁?auto 妯″紡锛歡roq 澶辫触鑷姩闄嶇骇 openai銆?

## B绔?/ Bilibili锛坆ili-cli 涓轰富锛孫penCLI 琛ュ瓧骞曪級

# REDACTED: sensitive-looking memory line

### 瑙嗛璇︽儏/鎼滅储/鐑棬/鎺掕 (bili-cli锛屽彧璇绘棤闇€鐧诲綍)

```bash
# 瑙嗛璇︽儏锛堟爣棰?UP涓?鏃堕暱/鎾斁浜掑姩鏁版嵁/瀛楀箷鍙敤鎬э級
bili video BVxxx

# 鎼滅储瑙嗛
bili search "query" --type video -n 5

# 鐑棬瑙嗛 / 鎺掕姒?
bili hot -n 10
bili rank -n 10

# 涓嬭浇闊抽骞跺垏鍒嗕负 ASR-ready WAV锛堟棤瀛楀箷鏃堕厤鍚?agent-reach transcribe 杞啓锛?
bili audio BVxxx
```

### 瀛楀箷 (OpenCLI锛岄渶瑕佹闈?Chrome)

```bash
# 瀛楀箷閫愬彞甯︽椂闂磋酱
opencli bilibili subtitle BVxxx

# OpenCLI 涔熻兘鎼滅储/璇昏棰戝厓鏁版嵁锛堝閫夛級
opencli bilibili search "query" -f yaml
opencli bilibili video BVxxx -f yaml
```

### 闆堕厤缃厹搴曪細鎼滅储 API 鐩磋繛

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
curl -s -c /tmp/bili_ck.txt -o /dev/null -A "$UA" "https://www.bilibili.com/"
curl -s -b /tmp/bili_ck.txt -A "$UA" -e "https://www.bilibili.com/" \
  "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=QUERY&page=1"
```

> **瀹夎 bili-cli**: `pipx install bilibili-cli`锛堜笂娓?2026-03 璧峰仠鏇翠絾瀹炴祴鍋ュ悍锛涘彧璇诲満鏅棤闇€鐧诲綍锛宍bili login` 鎵爜鍙В閿佸姩鎬?鏀惰棌绛変釜浜哄姛鑳斤級銆?

## 灏忓畤瀹欐挱瀹?/ Xiaoyuzhou Podcast

### 杞綍鍗曢泦鎾锛堝彲閫?--polish 澧炲己鏍囩偣锛?

```bash
# 杈撳嚭 Markdown 鏂囦欢鍒?/tmp/銆?-polish 璁?Llama 3.3 70B 缁欐枃绋胯ˉ涓枃鏍囩偣+鍚堢悊鍒嗘
~/.agent-reach/tools/xiaoyuzhou/transcribe.sh --polish "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"
```

> 杞啓 prompt 宸茶姹?Whisper 杈撳嚭涓枃鏍囩偣锛涜嫢鏍囩偣鏁堟灉浠嶄笉鐞嗘兂锛屽彲鍔?`--polish` 鐢?Groq 涓婂厤璐圭殑 Llama 3.3 70B 琛ユ爣鐐?鍚堢悊鍒嗘锛? 鍒嗛挓鎾绾﹀ ~7 绉掞級銆傛瘡娆¤浆鍐欏涓€杞?LLM 璋冪敤锛屾寜闇€浣跨敤銆?

### 鍓嶇疆瑕佹眰

1. **ffmpeg**: `brew install ffmpeg`
2. **Groq API Key** (鍏嶈垂): https://console.groq.com/keys
3. **閰嶇疆 Key**: `agent-reach configure groq-key YOUR_KEY`
4. **棣栨杩愯**: `agent-reach install --env=auto` 瀹夎宸ュ叿

### 妫€鏌ョ姸鎬?

```bash
agent-reach doctor
```

> 杈撳嚭 Markdown 鏂囦欢榛樿淇濆瓨鍒?`/tmp/`銆?

## 閫夋嫨鎸囧崡

| 鍦烘櫙 | 鎺ㄨ崘宸ュ叿 |
|-----|---------|
| YouTube 瀛楀箷 | yt-dlp |
| B绔欒棰戣鎯?鎼滅储 | bili-cli |
| B绔欏瓧骞?| opencli bilibili subtitle |
| 鎾杞綍 | 灏忓畤瀹?transcribe.sh |
| 鏃犲瓧骞曢煶瑙嗛 | agent-reach transcribe锛圔绔欓煶棰戝厛 `bili audio`锛?|
