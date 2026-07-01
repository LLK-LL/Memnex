$action = New-ScheduledTaskAction -Execute "wscript.exe" -Argument '"C:\Users\Administrator\total-agent-memory\scripts\start_tam_http_hidden.vbs"'
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId "Administrator" -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "TAM-Memory-HTTP-Server" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force
Write-Host "Scheduled task registered"
