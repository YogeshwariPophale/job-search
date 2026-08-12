param(
  [int]$Port = 8787,
  [string]$RefreshCommand = "",
  [int]$RefreshIntervalSeconds = 900,
  [switch]$UseApifyRefresh
)

$ErrorActionPreference = "Stop"

$TaskName = "Yogeshwari Job Search Live App"
$Script = Join-Path $PSScriptRoot "start_live_app.ps1"
$Args = "-NoProfile -ExecutionPolicy Bypass -File `"$Script`" -Port $Port -RefreshIntervalSeconds $RefreshIntervalSeconds"

if ($RefreshCommand.Trim()) {
  $Args += " -RefreshCommand `"$RefreshCommand`""
}

if ($UseApifyRefresh) {
  $Args += " -UseApifyRefresh"
}

$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $Args
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Keeps Yogeshwari's local job search app online after Windows login." -Force | Out-Null

Write-Host "Installed startup task: $TaskName"
Write-Host "It will start the live app after Windows login."
