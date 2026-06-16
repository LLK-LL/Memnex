# 缃戦〉闃呰

閫氱敤缃戦〉銆丷SS銆?

## 閫氱敤缃戦〉 (Jina Reader)

```bash
# 璇诲彇浠绘剰缃戦〉鍐呭
curl -s "https://r.jina.ai/URL"

# 绀轰緥
curl -s "https://r.jina.ai/https://example.com/article"
```

**閫傜敤鍦烘櫙**: 澶у鏁扮綉椤靛彲浠ョ洿鎺ョ敤 Jina Reader 璇诲彇銆?

## Web Reader (MCP)

```bash
# 璇诲彇缃戦〉鍐呭 (Markdown 鏍煎紡)
mcporter call 'web-reader.webReader(url: "https://example.com")'

# 淇濈暀鍥剧墖
mcporter call 'web-reader.webReader(url: "https://example.com", retain_images: true)'

# 绾枃鏈牸寮?
mcporter call 'web-reader.webReader(url: "https://example.com", return_format: "text")'
```

**閫傜敤鍦烘櫙**: 闇€瑕佹洿绮剧‘鎺у埗杈撳嚭鏍煎紡鏃朵娇鐢ㄣ€?

## RSS (feedparser)

```python
python3 -c "
import feedparser
for e in feedparser.parse('FEED_URL').entries[:5]:
    print(f'{e.title} 鈥?{e.link}')
"
```

**閫傜敤鍦烘櫙**: 璁㈤槄鍗氬銆佹柊闂绘簮銆佹挱瀹㈢瓑 RSS feed銆?

## 閫夋嫨鎸囧崡

| 鍦烘櫙 | 鎺ㄨ崘宸ュ叿 |
|-----|---------|
| 閫氱敤缃戦〉 | Jina Reader (`curl r.jina.ai`) |
| 闇€瑕佸浘鐗?鏍煎紡鎺у埗 | web-reader MCP |
| RSS 璁㈤槄 | feedparser |
