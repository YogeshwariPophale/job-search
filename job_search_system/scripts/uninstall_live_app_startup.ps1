$ErrorActionPreference = "Stop"

$TaskName = "Yogeshwari Job Search Live App"

if (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue) {
  Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
  Write-Host "Removed startup task: $TaskName"
} else {
  Write-Host "Startup task was not installed."
}
