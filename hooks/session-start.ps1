# SessionStart hook — remind Claude to use memory_recall + self_rules_context
#
# Add to %USERPROFILE%\.claude\settings.json:
#   "hooks": {
#     "SessionStart": [{
#       "type": "command",
#       "command": "powershell -ExecutionPolicy Bypass -File C:\\path\\to\\claude-total-memory\\hooks\\session-start.ps1"
#     }]
#   }

$Project = Split-Path -Leaf (Get-Location)
$Branch = ""
try { $Branch = (git rev-parse --abbrev-ref HEAD 2>$null) } catch {}

$Hint = "MEMORY_HINT: Project: $Project"
if ($Branch) { $Hint += ", Branch: $Branch" }
$Hint += ". Use memory_recall(query=`"your task`", project=`"$Project`") to search past knowledge."
$Hint += " Also run self_rules_context(project=`"$Project`", detail=`"compact`", query=`"your task`", top_k=5, include_always_on=true) to load query-ranked behavioral rules."

Write-Output $Hint
