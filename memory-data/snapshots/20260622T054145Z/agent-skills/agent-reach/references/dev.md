# 寮€鍙戝伐鍏?

GitHub CLI 

## GitHub (gh CLI)

GitHub 瀹樻柟鍛戒护琛屽伐鍏凤紝鐢ㄤ簬浠撳簱銆両ssue銆丳R銆丄ctions銆丷elease 浠ュ強 API 璁块棶銆?

```bash
# 璁よ瘉
# REDACTED: sensitive-looking memory line
# REDACTED: sensitive-looking memory line

# 鎼滅储
gh search repos "query" --sort stars --limit 10
gh search code "query" --language python

# 浠撳簱
gh repo view owner/repo
gh repo clone owner/repo
gh repo create my-repo --private
gh repo fork owner/repo
gh repo fork owner/repo --clone
gh repo sync owner/repo

# Issues
gh issue list -R owner/repo --state open
gh issue view 123 -R owner/repo
gh issue create -R owner/repo --title "Title" --body "Body"

# Pull Requests
gh pr list -R owner/repo --state open
gh pr view 123 -R owner/repo
gh pr create -R owner/repo --title "Title" --body "Body"
gh pr checks 123 --repo owner/repo

# Actions / CI
gh run list --repo owner/repo --limit 10
gh run view <run-id> --repo owner/repo
gh run view <run-id> --repo owner/repo --log-failed
gh workflow list --repo owner/repo

# Releases
gh release list -R owner/repo
gh release create v1.0.0

# API
gh api /user
gh api repos/owner/repo

# JSON 杈撳嚭
gh issue list --repo owner/repo --json number,title --jq '.[] | "\(.number): \(.title)"'
```


## 閫夋嫨鎸囧崡

| 宸ュ叿 | 鏉ユ簮 | 鐢ㄩ€?|
|-----|------|------|
| gh CLI | agent-reach | Git 鎿嶄綔 |
| zread | my-mcp-tools | 璇讳粨搴撳唴瀹?|
| context7 | my-mcp-tools | 鏌ユ妧鏈枃妗?|
