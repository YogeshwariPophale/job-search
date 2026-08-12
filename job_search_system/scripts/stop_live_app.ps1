$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$PidFile = Join-Path $Root "job_search_system\tmp\live_server.pid"

if (-not (Test-Path $PidFile)) {
  Write-Host "No live app PID file found."
  exit 0
}

$PidValue = Get-Content -LiteralPath $PidFile -ErrorAction SilentlyContinue
if ($PidValue -and (Get-Process -Id $PidValue -ErrorAction SilentlyContinue)) {
  Stop-Process -Id $PidValue
  Write-Host "Stopped live app PID $PidValue"
} else {
  Write-Host "Live app process was not running."
}

Remove-Item -LiteralPath $PidFile -Force
