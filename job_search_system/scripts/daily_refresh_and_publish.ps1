<#
.SYNOPSIS
  Runs the job search daily refresh pipeline, then commits and pushes any
  changed source data files to GitHub so the GitHub Pages job board
  (deploy-pages.yml) redeploys automatically with fresh data every day.

.USAGE
  Save this into job_search_system/scripts/daily_refresh_and_publish.ps1
  Then either run it manually:

    powershell -ExecutionPolicy Bypass -File job_search_system/scripts/daily_refresh_and_publish.ps1

  ...or point the scheduled task at it instead of run_daily_refresh.py directly
  (see install_daily_refresh_task.ps1 -Publish switch below).

.NOTES
  - Requires that `git push` already works non-interactively from this machine
    for this user (i.e. you are NOT prompted for a username/password/token
    when you push manually right now). If you use HTTPS + a Personal Access
    Token, make sure Git Credential Manager has it cached (a normal manual
    `git push` once will cache it). If you use SSH, make sure the key has no
    passphrase prompt, or is loaded in ssh-agent/Pageant at task run time.
  - Only commits if there are actual changes, so it's safe to run daily even
    if nothing new was found.
#>

param(
  [string]$CommitMessage = ""
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$System = Join-Path $Root "job_search_system"
$RefreshScript = Join-Path $System "scripts\run_daily_refresh.py"
$LogFile = Join-Path $System "tmp\daily_refresh_and_publish.log"

New-Item -ItemType Directory -Force -Path (Split-Path $LogFile) | Out-Null

function Log($message) {
  $stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $line = "[$stamp] $message"
  Write-Host $line
  Add-Content -LiteralPath $LogFile -Value $line
}

$Python = "C:\Users\hp\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path $Python)) {
  $Python = "python"
}

Set-Location $Root

Log "=== Daily refresh + publish starting ==="

# 1. Run the refresh pipeline (same as "Run my daily job refresh")
try {
  Log "Running refresh pipeline: $RefreshScript"
  $output = & $Python $RefreshScript 2>&1 | Out-String
  Add-Content -LiteralPath $LogFile -Value $output
  Log "Refresh pipeline finished."
} catch {
  Log "Refresh pipeline FAILED: $_"
  Log "Aborting publish step; will not push a broken/partial state."
  exit 1
}

# 2. Make sure we're not behind origin before committing, to avoid push rejections
try {
  Log "Fetching latest from origin..."
  git fetch origin master 2>&1 | Out-String | ForEach-Object { Add-Content -LiteralPath $LogFile -Value $_ }

  $behindCount = (git rev-list --count HEAD..origin/master).Trim()
  if ($behindCount -ne "0") {
    Log "Local branch is $behindCount commit(s) behind origin/master. Attempting fast-forward pull..."
    git pull --ff-only origin master 2>&1 | Out-String | ForEach-Object { Add-Content -LiteralPath $LogFile -Value $_ }
  }
} catch {
  Log "WARNING: could not fetch/pull cleanly: $_"
  Log "Continuing anyway; push may fail below if there's a real conflict."
}

# 3. Stage only the source data the online board reads.
$PathsToStage = @(
  "job_search_system/data"
) | Where-Object { Test-Path (Join-Path $Root $_) }

if ($PathsToStage.Count -eq 0) {
  Log "No known source data paths exist to stage. Nothing to publish."
  exit 0
}

git add $PathsToStage 2>&1 | Out-String | ForEach-Object { Add-Content -LiteralPath $LogFile -Value $_ }

# 4. Check if there's actually anything to commit
$statusOutput = git status --porcelain -- $PathsToStage
if (-not $statusOutput) {
  Log "No changes after refresh. Nothing to commit or push today."
  Log "=== Daily refresh + publish finished (no-op) ==="
  exit 0
}

# 5. Commit and push
$today = Get-Date -Format "yyyy-MM-dd"
if (-not $CommitMessage.Trim()) {
  $CommitMessage = "Daily job refresh - $today"
}

try {
  git commit -m $CommitMessage 2>&1 | Out-String | ForEach-Object { Add-Content -LiteralPath $LogFile -Value $_ }
  Log "Committed: $CommitMessage"

  git push origin master 2>&1 | Out-String | ForEach-Object { Add-Content -LiteralPath $LogFile -Value $_ }
  Log "Pushed to origin/master. GitHub Pages should redeploy shortly."
} catch {
  Log "Commit/push FAILED: $_"
  Log "Data was refreshed locally but NOT published. Check git status manually."
  exit 1
}

Log "=== Daily refresh + publish finished ==="
