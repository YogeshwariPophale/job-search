@echo off
cd /d "%~dp0\..\.."
start "Yogeshwari Job Search Live App" /min powershell.exe -NoProfile -ExecutionPolicy Bypass -File "job_search_system\scripts\start_live_app.ps1" -UseApifyRefresh
