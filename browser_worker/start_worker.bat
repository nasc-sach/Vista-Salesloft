@echo off
setlocal
cd /d "%~dp0\.."

if not defined BROWSER_WORKER_TOKEN (
  set "BROWSER_WORKER_TOKEN=vista-dev-token-change-me"
)
if not defined BROWSER_WORKER_ALLOWED_HOSTS (
  set "BROWSER_WORKER_ALLOWED_HOSTS=vistapoc.nitor.in"
)
if not defined PORT (
  set "PORT=8787"
)

echo Starting Vista Browser Worker on http://0.0.0.0:%PORT%
echo Token auth: ON (BROWSER_WORKER_TOKEN is set)
echo Allowed hosts: %BROWSER_WORKER_ALLOWED_HOSTS%
echo.
echo Next: run tunnel in another terminal:
echo   browser_worker\start_tunnel.bat
echo.
echo Then set in AAVA:
echo   BROWSER_WORKER_URL=^<public https url from tunnel^>
echo   BROWSER_WORKER_TOKEN=%BROWSER_WORKER_TOKEN%
echo.

".\.venv\Scripts\python.exe" -m uvicorn browser_worker.main:app --host 0.0.0.0 --port %PORT%
