# Vista Browser Worker (for AAVA)

AAVA cannot run Playwright. This worker runs Playwright on your machine and exposes `POST /v1/explore`. Tunnel it so AAVA can reach it.

## 1) Install deps (once)

```powershell
cd E:\Vista-SalesLoft
.\.venv\Scripts\python.exe -m pip install -r browser_worker\requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

Install a tunnel client (pick one):

```powershell
winget install Cloudflare.cloudflared
# or
winget install Ngrok.Ngrok
```

## 2) Start worker (terminal 1)

```powershell
browser_worker\start_worker.bat
```

Default: `http://127.0.0.1:8787`  
Default token: `vista-dev-token-change-me`  
Allowlist: `vistapoc.nitor.in`

## 3) Start tunnel (terminal 2)

```powershell
browser_worker\start_tunnel.bat
```

Copy the public HTTPS URL, e.g. `https://random-words.trycloudflare.com`.

## 4) Configure AAVA

```text
BROWSER_WORKER_URL=https://random-words.trycloudflare.com
BROWSER_WORKER_TOKEN=vista-dev-token-change-me
```

Keep token identical on worker and AAVA.

## 5) Smoke test locally

```powershell
curl http://127.0.0.1:8787/health

curl -X POST http://127.0.0.1:8787/v1/explore ^
  -H "Authorization: Bearer vista-dev-token-change-me" ^
  -H "Content-Type: application/json" ^
  -d "{\"session_id\":\"demo\",\"url\":\"https://vistapoc.nitor.in/login\",\"action\":\"Navigate\"}"
```

## Agent flow tip

Reuse the same `session_id` for:

1. Navigate login page  
2. Type username  
3. Type password  
4. Click Sign In  
5. Click Staff Management / Weekly Roster / …

## Security notes

- Set a strong `BROWSER_WORKER_TOKEN`
- Keep `BROWSER_WORKER_ALLOWED_HOSTS` set (SSRF protection)
- Quick tunnels are for POC; prefer a named tunnel/VM for longer use
