#!/usr/bin/env bash
set -euo pipefail

# serper-search.sh - Serper API 搜索辅助脚本
# 用法: ./serper-search.sh <查询词> [国家代码] [语言] [时间范围] [数量] [页码]
#
# 示例:
#   ./serper-search.sh "OpenAI GPT-5"
#   ./serper-search.sh "Claude 4" "us" "en" "qdr:w" 5
#   ./serper-search.sh "人工智能" "cn" "zh-cn" "qdr:m" 10

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "${SERPER_API_KEY:-}" ]; then
  echo "错误: 环境变量 SERPER_API_KEY 未设置" >&2
  echo "请先设置: export SERPER_API_KEY='your-api-key'" >&2
  exit 1
fi

QUERY="${1:-}"
GL="${2:-us}"
HL="${3:-en}"
TBS="${4:-}"
NUM="${5:-10}"
PAGE="${6:-1}"

if [ -z "$QUERY" ]; then
  echo "错误: 请提供搜索关键词" >&2
  echo "用法: $0 <查询词> [国家代码] [语言] [时间范围] [数量] [页码]" >&2
  exit 1
fi

# 构建请求体
BODY=$(cat <<JSON
{
  "q": "$QUERY",
  "gl": "$GL",
  "hl": "$HL",
  "num": $NUM,
  "page": $PAGE
}
JSON
)

# 添加时间范围（如果提供）
if [ -n "$TBS" ]; then
  BODY=$(echo "$BODY" | sed "s/}$/, \"tbs\": \"$TBS\" }/")
fi

# 调用 Serper Search API
RESPONSE=$(curl -s --location 'https://google.serper.dev/search' \
  --header "X-API-KEY: $SERPER_API_KEY" \
  --header 'Content-Type: application/json' \
  --data "$BODY")

# 检查 API 返回是否有错误
if echo "$RESPONSE" | head -1 | grep -q "error"; then
  echo "API 错误: $RESPONSE" >&2
  exit 1
fi

echo "$RESPONSE"
