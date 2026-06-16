#!/usr/bin/env bash
set -euo pipefail

# serper-scrape.sh - Serper API 缃戦〉鎶撳彇杈呭姪鑴氭湰
# 鐢ㄦ硶: ./serper-scrape.sh <URL> [includeMarkdown]
#
# 绀轰緥:
#   ./serper-scrape.sh "https://example.com"
#   ./serper-scrape.sh "https://example.com" true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
  exit 1
fi

URL="${1:-}"
INCLUDE_MD="${2:-true}"

if [ -z "$URL" ]; then
  echo "閿欒: 璇锋彁渚涚洰鏍?URL" >&2
  echo "鐢ㄦ硶: $0 <URL> [includeMarkdown]" >&2
  exit 1
fi

# 妫€鏌?URL 鏍煎紡
if [[ ! "$URL" =~ ^https?:// ]]; then
  echo "閿欒: URL 蹇呴』浠?http:// 鎴?https:// 寮€澶? >&2
  exit 1
fi

# 鏋勫缓璇锋眰浣?BODY=$(cat <<JSON
{
  "url": "$URL",
  "includeMarkdown": $INCLUDE_MD
}
JSON
)

# 璋冪敤 Serper Scrape API
RESPONSE=$(curl -s --location 'https://scrape.serper.dev' \
# REDACTED: sensitive-looking memory line
  --header 'Content-Type: application/json' \
  --data "$BODY")

# 妫€鏌?API 杩斿洖鏄惁鏈夐敊璇?if echo "$RESPONSE" | head -1 | grep -q "error"; then
  echo "API 閿欒: $RESPONSE" >&2
  exit 1
fi

echo "$RESPONSE"
