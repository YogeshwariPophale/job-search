<#
.SYNOPSIS
  Installs a Windows Scheduled Task that runs Yogeshwari's job search
  daily refresh pipeline automatically once a day, independent of whether
  the live app or browser is open.

  By default it now runs daily_refresh_and_publish.ps1, which refreshes
  the data AND commits/pushes it to GitHub, so the GitHub Pages job board
  redeploys with fresh jobs every day.

.USAGE
  Save this file into job_search_system/scripts/install_daily_refresh_task.ps1
  then run from the workspace root:

    powershell -ExecutionPolicy Bypass -File job_search_system/scripts/install_daily_refresh_task.ps1

  Choose a different run time (24h format, local time):

    powershell -ExecutionPolicy Bypass -File job_search_system/scripts/install_daily_refresh_task.ps1 -Time "06:30"

  Refresh data locally only, without pushing to GitHub (old behavior):

    powershell -ExecutionPolicy Bypass -File job_search_system/scripts/install_daily_refresh_task.ps1 -PublishToGitHub:$false
#>

param(
  [string]$Time = "07:00",
  [string]$TaskName = "Yogeshwari Job Search Daily Refresh",
  [bool]$PublishToGitHub = $true
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$System = Join-Path $Root "job_search_system"

if ($PublishToGitHub) {
  $TargetScript = Join-Path $System "scripts\daily_refresh_and_publish.ps1"
  if (-not (Test-Path $TargetScript)) {
    throw "Could not find $TargetScript. Save daily_refresh_and_publish.ps1 into job_search_system/scripts/ first."
  }
  $LogFile = Join-Path $System "tmp\daily_refresh_task_powershell.log"
  New-Item -ItemType Directory -Force -Path (Split-Path $LogFile) | Out-Null

  # Run via powershell.exe so publish step (git commands, error handling) executes correctly.
  $WrapperArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$TargetScript`""
  $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $WrapperArgs -WorkingDirectory $Root
  $Description = "Runs Yogeshwari's job_search_system daily refresh AND publishes updated data to GitHub Pages once a day."
} else {
  $RefreshScript = Join-Path $System "scripts\run_daily_refresh.py"
  if (-not (Test-Path $RefreshScript)) {
    throw "Could not find $RefreshScript. Run this script from inside the job_search_system workspace."
  }
  $LogFile = Join-Path $System "tmp\daily_refresh_task.log"
  New-Item -ItemType Directory -Force -Path (Split-Path $LogFile) | Out-Null

  $Python = "C:\Users\hp\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
  if (-not (Test-Path $Python)) {
    $Python = "python"
  }

  $WrapperArgs = "/c `"`"$Python`" `"$RefreshScript`" >> `"$LogFile`" 2>&1`""
  $Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $WrapperArgs -WorkingDirectory $Root
  $Description = "Runs Yogeshwari's job_search_system daily refresh pipeline locally only (no GitHub publish)."
}

$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -StartWhenAvailable `
  -WakeToRun

Register-ScheduledTask -TaskName $TaskName `
  -Action $Action `
  -Trigger $Trigger `
  -Settings $Settings `
  -Description $Description `
  -Force | Out-Null

Write-Host "Installed scheduled task: $TaskName"
Write-Host "It will run every day at $Time."
if ($PublishToGitHub) {
  Write-Host "Mode: refresh + publish to GitHub (job board will update automatically)."
} else {
  Write-Host "Mode: local refresh only (data will NOT be pushed to GitHub automatically)."
}
Write-Host "Log file: $LogFile"
Write-Host ""
Write-Host "To run it right now instead of waiting for $Time, use:"
Write-Host "  Start-ScheduledTask -TaskName `"$TaskName`""
Write-Host ""
Write-Host "To remove it later:"
Write-Host "  Unregister-ScheduledTask -TaskName `"$TaskName`" -Confirm:`$false"
