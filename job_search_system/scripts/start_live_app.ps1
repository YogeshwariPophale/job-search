param(
  [int]$Port = 8787,
  [string]$RefreshCommand = "",
  [int]$RefreshIntervalSeconds = 900,
  [switch]$UseApifyRefresh
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$System = Join-Path $Root "job_search_system"
$PidFile = Join-Path $System "tmp\live_server.pid"
$Python = "C:\Users\hp\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (-not (Test-Path $Python)) {
  $Python = "python"
}

New-Item -ItemType Directory -Force -Path (Split-Path $PidFile) | Out-Null

@(
  "APIFY_TOKEN",
  "APIFY_ACTOR_ID",
  "APIFY_TASK_ID",
  "APIFY_DATASET_ID",
  "APIFY_INPUT_FILE",
  "APIFY_RUN_TIMEOUT_SECONDS"
) | ForEach-Object {
  $Value = [Environment]::GetEnvironmentVariable($_, "User")
  if ($null -ne $Value -and $Value.Trim()) {
    [Environment]::SetEnvironmentVariable($_, $Value, "Process")
  }
}

if (Test-Path $PidFile) {
  $OldPid = Get-Content -LiteralPath $PidFile -ErrorAction SilentlyContinue
  if ($OldPid -and (Get-Process -Id $OldPid -ErrorAction SilentlyContinue)) {
    Write-Host "Live app already running with PID $OldPid"
    Write-Host "Phone URL: http://$((ipconfig | Select-String 'IPv4 Address' | Select-Object -First 1).ToString().Split(':')[-1].Trim()):$Port/job_search_system/phone_app.html"
    exit 0
  }
}

$ArgsList = @(
  (Join-Path $System "scripts\live_server.py"),
  "--port", "$Port",
  "--refresh-interval", "$RefreshIntervalSeconds"
)

if ($UseApifyRefresh) {
  $ArgsList += @("--use-apify-refresh")
}

if ($RefreshCommand.Trim()) {
  $ArgsList += @("--refresh-command", $RefreshCommand)
}

$Process = Start-Process -FilePath $Python -ArgumentList $ArgsList -WorkingDirectory $Root -WindowStyle Hidden -PassThru
$Process.Id | Set-Content -LiteralPath $PidFile

$IpLine = ipconfig | Select-String "IPv4 Address" | Select-Object -First 1
$Ip = if ($IpLine) { $IpLine.ToString().Split(":")[-1].Trim() } else { "YOUR-COMPUTER-IP" }

Write-Host "Live app started with PID $($Process.Id)"
Write-Host "Desktop URL: http://127.0.0.1:$Port/job_search_system/phone_app.html"
Write-Host "Phone URL:   http://$Ip`:$Port/job_search_system/phone_app.html"
