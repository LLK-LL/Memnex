#!/usr/bin/env bash
set -euo pipefail

# serper-scrape.sh - Serper API 网页抓取辅助脚本
# 用法: ./serper-scrape.sh <URL> [includeMarkdown]
#
# 示例:
#   ./serper-scrape.sh "https://example.com"
#   ./serper-scrape.sh "https://example.com" true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "${SERPER_API_KEY:-}" ]; then
  echo "错误: 环境变量 SERPER_API_KEY 未设置" >&2
  echo "请先设置: export SERPER_API_KEY='your-api-key'" >&2
  exit 1
fi

URL="${1:-}"
INCLUDE_MD="${2:-true}"

if [ -z "$URL" ]; then
  echo "错误: 请提供目标 URL" >&2
  echo "用法: $0 <URL> [includeMarkdown]" >&2
  exit 1
fi

# 检查 URL 格式
if [[ ! "$URL" =~ ^https?:// ]]; then
  echo "错误: URL 必须以 http:// 或 https:// 开头" >&2
  exit 1
fi

# 构建请求体
BODY=$(cat <<JSON
{
  "url": "$URL",
  "includeMarkdown": $INCLUDE_MD
}
JSON
)

# 调用 Serper Scrape API
RESPONSE=$(curl -s --location 'https://scrape.serper.dev' \
  --header "X-API-KEY: $SERPER_API_KEY" \
  --header 'Content-Type: application/json' \
  --data "$BODY")

# 检查 API 返回是否有错误
if echo "$RESPONSE" | head -1 | grep -q "error"; then
  echo "API 错误: $RESPONSE" >&2
  exit 1
fi

echo "$RESPONSE"
