#!/usr/bin/env bash
set -euo pipefail

# serper-search.sh - Serper API 鎼滅储杈呭姪鑴氭湰
# 鐢ㄦ硶: ./serper-search.sh <鏌ヨ璇? [鍥藉浠ｇ爜] [璇█] [鏃堕棿鑼冨洿] [鏁伴噺] [椤电爜]
#
# 绀轰緥:
#   ./serper-search.sh "OpenAI GPT-5"
#   ./serper-search.sh "Claude 4" "us" "en" "qdr:w" 5
#   ./serper-search.sh "浜哄伐鏅鸿兘" "cn" "zh-cn" "qdr:m" 10

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line
  exit 1
fi

QUERY="${1:-}"
GL="${2:-us}"
HL="${3:-en}"
TBS="${4:-}"
NUM="${5:-10}"
PAGE="${6:-1}"

if [ -z "$QUERY" ]; then
  echo "閿欒: 璇锋彁渚涙悳绱㈠叧閿瘝" >&2
  echo "鐢ㄦ硶: $0 <鏌ヨ璇? [鍥藉浠ｇ爜] [璇█] [鏃堕棿鑼冨洿] [鏁伴噺] [椤电爜]" >&2
  exit 1
fi

# 鏋勫缓璇锋眰浣?BODY=$(cat <<JSON
{
  "q": "$QUERY",
  "gl": "$GL",
  "hl": "$HL",
  "num": $NUM,
  "page": $PAGE
}
JSON
)

# 娣诲姞鏃堕棿鑼冨洿锛堝鏋滄彁渚涳級
if [ -n "$TBS" ]; then
  BODY=$(echo "$BODY" | sed "s/}$/, \"tbs\": \"$TBS\" }/")
fi

# 璋冪敤 Serper Search API
RESPONSE=$(curl -s --location 'https://google.serper.dev/search' \
# REDACTED: sensitive-looking memory line
  --header 'Content-Type: application/json' \
  --data "$BODY")

# 妫€鏌?API 杩斿洖鏄惁鏈夐敊璇?if echo "$RESPONSE" | head -1 | grep -q "error"; then
  echo "API 閿欒: $RESPONSE" >&2
  exit 1
fi

echo "$RESPONSE"
