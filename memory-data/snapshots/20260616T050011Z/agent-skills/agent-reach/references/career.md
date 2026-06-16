# 鑱屽満鎷涜仒

LinkedIn銆?

## LinkedIn

```bash
# 鑾峰彇涓汉璧勬枡
mcporter call 'linkedin-scraper.get_person_profile(linkedin_url: "https://linkedin.com/in/username")'

# 鎼滅储浜烘墠
mcporter call 'linkedin-scraper.search_people(keyword: "AI engineer", limit: 10)'

# 鑾峰彇鍏徃璧勬枡
mcporter call 'linkedin-scraper.get_company_profile(linkedin_url: "https://linkedin.com/company/xxx")'

# 鎼滅储鑱屼綅
mcporter call 'linkedin-scraper.search_jobs(keyword: "software engineer", limit: 10)'
```

> **闇€瑕佺櫥褰?*: LinkedIn scraper 闇€瑕佹湁鏁堢殑鐧诲綍鎬併€?

### Fallback 鏂规

濡傛灉 MCP 涓嶅彲鐢紝鍙互鐢?Jina Reader锛?

```bash
curl -s "https://r.jina.ai/https://linkedin.com/in/username"
```
