@echo off
setlocal
cd /d "%~dp0\.."

if not defined PORT set "PORT=8787"

set "CLOUDFLARED="
where cloudflared >nul 2>&1 && set "CLOUDFLARED=cloudflared"
if not defined CLOUDFLARED if exist "%ProgramFiles(x86)%\cloudflared\cloudflared.exe" set "CLOUDFLARED=%ProgramFiles(x86)%\cloudflared\cloudflared.exe"
if not defined CLOUDFLARED if exist "%ProgramFiles%\cloudflared\cloudflared.exe" set "CLOUDFLARED=%ProgramFiles%\cloudflared\cloudflared.exe"

if defined CLOUDFLARED (
  echo Using cloudflared quick tunnel -^> http://127.0.0.1:%PORT%
  echo.
  echo Copy the https://*.trycloudflare.com URL into AAVA:
  echo   BROWSER_WORKER_URL=^<that https url^>
  echo   BROWSER_WORKER_TOKEN=vista-dev-token-change-me
  echo.
  "%CLOUDFLARED%" tunnel --url http://127.0.0.1:%PORT%
  goto :eof
)

where ngrok >nul 2>&1
if %ERRORLEVEL%==0 (
  echo Using ngrok tunnel -^> http://127.0.0.1:%PORT%
  echo Copy the https forwarding URL into AAVA BROWSER_WORKER_URL
  ngrok http %PORT%
  goto :eof
)

echo Neither cloudflared nor ngrok was found.
echo Install with: winget install Cloudflare.cloudflared
exit /b 1
