param(
  [Parameter(Mandatory=$true)]
  [string]$ApifyToken,

  [string]$ActorId = "",
  [string]$TaskId = "",
  [string]$DatasetId = "",
  [string]$InputFile = "job_search_system/connectors/apify_linkedin_data_analyst_input.json"
)

$ErrorActionPreference = "Stop"

[Environment]::SetEnvironmentVariable("APIFY_TOKEN", $ApifyToken, "User")
[Environment]::SetEnvironmentVariable("APIFY_ACTOR_ID", $ActorId, "User")
[Environment]::SetEnvironmentVariable("APIFY_TASK_ID", $TaskId, "User")
[Environment]::SetEnvironmentVariable("APIFY_DATASET_ID", $DatasetId, "User")
[Environment]::SetEnvironmentVariable("APIFY_INPUT_FILE", $InputFile, "User")

Write-Host "Saved Apify refresh settings to your Windows user environment."
Write-Host "Restart the live app or log out/in for startup-launched processes to see the new values."
