# SessionStart hook — remind Claude to use memory_recall + rule_context_refresh
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
$Hint += " Also run rule_context_refresh(project=`"$Project`", detail=`"compact`", phase=`"build`", event=`"task_start`", latest_user_instruction=`"your task`") to load query-ranked behavioral rules."

Write-Output $Hint
