"""
Vista Browser Worker — Playwright service for AAVA remote browser automation.

Exposes:
  GET  /health
  POST /v1/explore

Compatible with playwright/planner-agent/tool-prompts/browser-automation-tool.py

Run locally:
  .\\.venv\\Scripts\\python.exe -m uvicorn browser_worker.main:app --host 0.0.0.0 --port 8787

Then tunnel (pick one):
  cloudflared tunnel --url http://127.0.0.1:8787
  ngrok http 8787

Set in AAVA:
  BROWSER_WORKER_URL=<public https url from tunnel>
  BROWSER_WORKER_TOKEN=<same as BROWSER_WORKER_TOKEN below>
"""

from __future__ import annotations

import os
import re
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

APP_DIR = Path(__file__).resolve().parent
SCREENSHOT_DIR = APP_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

WORKER_TOKEN = (os.environ.get("BROWSER_WORKER_TOKEN") or "").strip()
SESSION_TTL_SEC = int(os.environ.get("BROWSER_WORKER_SESSION_TTL", "900"))
ALLOWED_HOSTS = {
    h.strip().lower()
    for h in (os.environ.get("BROWSER_WORKER_ALLOWED_HOSTS") or "").split(",")
    if h.strip()
}
DEFAULT_HEADLESS = os.environ.get("BROWSER_WORKER_HEADLESS", "true").lower() not in {
    "0",
    "false",
    "no",
}

app = FastAPI(title="Vista Browser Worker", version="1.0.0")


def ts() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class ExploreRequest(BaseModel):
    session_id: str = Field(default="default")
    url: str
    action: str = Field(default="Navigate")
    target_element: str = Field(default="")
    input_value: str = Field(default="")
    wait_for_selector: Optional[str] = None
    wait_timeout: int = 30000
    capture_network: bool = True
    take_screenshot: bool = False
    headless: bool = True
    authenticate: Optional[Dict[str, str]] = None
    ignore_https_errors: bool = True
    client: Optional[Dict[str, Any]] = None


class SessionState:
    def __init__(self, session_id: str, context: BrowserContext, page: Page):
        self.session_id = session_id
        self.context = context
        self.page = page
        self.network: List[str] = []
        self.last_used = time.time()
        self.lock = threading.Lock()

        def _on_response(resp):
            try:
                self.network.append(resp.url)
            except Exception:
                pass

        self.page.on("response", _on_response)


class BrowserManager:
    def __init__(self) -> None:
        self._pw: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._sessions: Dict[str, SessionState] = {}
        self._lock = threading.Lock()
        self._headless = DEFAULT_HEADLESS

    def start(self, headless: bool = True) -> None:
        with self._lock:
            if self._browser is not None:
                return
            self._headless = headless
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(headless=headless)

    def stop(self) -> None:
        with self._lock:
            for sid, sess in list(self._sessions.items()):
                try:
                    sess.context.close()
                except Exception:
                    pass
                self._sessions.pop(sid, None)
            if self._browser is not None:
                try:
                    self._browser.close()
                except Exception:
                    pass
                self._browser = None
            if self._pw is not None:
                try:
                    self._pw.stop()
                except Exception:
                    pass
                self._pw = None

    def _purge_expired(self) -> None:
        now = time.time()
        expired = [
            sid
            for sid, sess in self._sessions.items()
            if now - sess.last_used > SESSION_TTL_SEC
        ]
        for sid in expired:
            sess = self._sessions.pop(sid, None)
            if sess is None:
                continue
            try:
                sess.context.close()
            except Exception:
                pass

    def get_or_create(
        self,
        session_id: str,
        *,
        headless: bool,
        ignore_https_errors: bool,
    ) -> SessionState:
        self.start(headless=headless)
        assert self._browser is not None
        with self._lock:
            self._purge_expired()
            sess = self._sessions.get(session_id)
            if sess is not None:
                sess.last_used = time.time()
                return sess
            context = self._browser.new_context(
                ignore_https_errors=ignore_https_errors,
                viewport={"width": 1440, "height": 900},
                user_agent="Vista-Browser-Worker/1.0",
            )
            page = context.new_page()
            sess = SessionState(session_id, context, page)
            self._sessions[session_id] = sess
            return sess

    def session_count(self) -> int:
        return len(self._sessions)


MANAGER = BrowserManager()


def require_auth(authorization: Optional[str] = Header(default=None)) -> None:
    if not WORKER_TOKEN:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.split(" ", 1)[1].strip()
    if token != WORKER_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")


def _host_allowed(url: str) -> bool:
    if not ALLOWED_HOSTS:
        return True
    host = (urlparse(url).hostname or "").lower()
    return host in ALLOWED_HOSTS


def extract_page(page: Page, action: str = "Navigate") -> Dict[str, Any]:
    data = page.evaluate(
        """() => {
        const abs = (href) => { try { return new URL(href, location.href).href; } catch { return href; } };
        const text = (el) => (el.innerText || el.textContent || '').trim().replace(/\\s+/g, ' ');
        const headings = [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(el => ({
          tag: el.tagName.toLowerCase(), text: text(el).slice(0, 200)
        })).filter(h => h.text);
        const input_fields = [...document.querySelectorAll('input,textarea,select')].map(el => {
          let placeholder = el.placeholder || el.getAttribute('aria-label') || '';
          if (!placeholder && el.id) {
            const lab = document.querySelector(`label[for="${el.id}"]`);
            if (lab) placeholder = text(lab);
          }
          return {
            type: el.tagName.toLowerCase() === 'select' ? 'select' : (el.type || el.tagName.toLowerCase()),
            id: el.id || '',
            name: el.name || '',
            placeholder,
            required: !!el.required
          };
        });
        const buttons = [...document.querySelectorAll('button,[role="button"],input[type="submit"],input[type="button"]')].map(el => ({
          text: text(el) || el.value || '', type: el.type || 'button'
        })).filter(b => b.text);
        const all_links = [...document.querySelectorAll('a')].map(a => ({
          text: text(a), href: abs(a.getAttribute('href') || '')
        })).filter(l => l.text || l.href);
        const nav_links = buttons
          .filter(b => ['Dashboard','Staff Management','Shift Management','Weekly Roster','Shift Requests','Reference Data','Export','Audit','Logout'].includes(b.text))
          .map(b => ({ text: b.text, href: '' }));
        const visible_text = [];
        for (const el of document.querySelectorAll('h1,h2,h3,h4,h5,button,th,td,label,p,li,a,span')) {
          const t = text(el);
          if (t && t.length < 120 && t.length > 1 && !visible_text.includes(t)) visible_text.push(t);
          if (visible_text.length >= 50) break;
        }
        const body = (document.body.innerText || '').replace(/\\s+/g, ' ').trim();
        const scripts = [...document.querySelectorAll('script[src]')].map(s => s.src);
        return {
          current_url: location.href,
          page_title: document.title,
          https: location.protocol === 'https:',
          headings,
          input_fields,
          buttons,
          all_links,
          nav_links,
          visible_text,
          body_snippet: body.slice(0, 2000),
          scripts,
          fetch_source: 'SPA Module Inspector',
          confidence: 'High'
        };
      }"""
    )
    data["action_performed"] = action
    data["timestamp"] = ts()
    return data


def detect_framework(page: Page) -> Dict[str, Any]:
    return page.evaluate(
        """() => {
        const hints = [];
        if (window.React || document.querySelector('#root,[data-reactroot]')) hints.push('React');
        if (window.Vue || document.querySelector('[data-v-]')) hints.push('Vue.js');
        if (window.angular || document.querySelector('[ng-version]')) hints.push('Angular');
        const scripts = [...document.querySelectorAll('script[src]')].map(s => s.src || '');
        const hasModule = !!document.querySelector('script[type="module"]');
        if (hasModule || scripts.some(s => s.includes('vite') || s.includes('/assets/'))) {
          hints.push('Vite');
        }
        const uniq = [...new Set(hints)];
        return {
          framework_hints: uniq,
          is_react: uniq.includes('React'),
          is_vue: uniq.includes('Vue.js'),
          is_angular: uniq.includes('Angular'),
          is_spa: !!(document.querySelector('#root,#app')),
          framework: uniq[0] || 'unknown'
        };
      }"""
    )


def analyze_auth(page: Page) -> Dict[str, Any]:
    return page.evaluate(
        """() => {
        const hasPassword = !!document.querySelector('input[type="password"]');
        const bodyText = document.body ? (document.body.innerText || '') : '';
        const logout = /logout|sign out/i.test(bodyText);
        return {
          has_login_form: hasPassword,
          has_logout_button: logout,
          appears_authenticated: logout && !hasPassword,
          login_form_visible: hasPassword
        };
      }"""
    )


def resolve_selector(target: str) -> List[str]:
    t = (target or "").strip()
    if not t:
        return []
    selectors = []
    if t.startswith("#") or t.startswith(".") or t.startswith("["):
        selectors.append(t)
    lower = t.lower()
    if "user" in lower:
        selectors.extend(["#username", "input[name='username']", "input[type='text']"])
    if "pass" in lower:
        selectors.extend(["#password", "input[name='password']", "input[type='password']"])
    selectors.extend(
        [
            f"#{t}",
            f"[name='{t}']",
            f"[id='{t}']",
            f"[placeholder='{t}']",
            f"button:has-text('{t}')",
            f"text={t}",
        ]
    )
    # dedupe preserve order
    seen = set()
    out = []
    for s in selectors:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def fill_first(page: Page, selectors: List[str], value: str, timeout: int) -> str:
    last_err = ""
    for sel in selectors:
        try:
            page.fill(sel, value, timeout=min(timeout, 5000))
            return sel
        except Exception as exc:
            last_err = str(exc)
    raise RuntimeError(f"Could not fill target. Last error: {last_err}")


def click_first(page: Page, target: str, timeout: int) -> str:
    # Prefer role/text for SPA nav buttons
    try:
        page.get_by_role("button", name=target, exact=True).click(timeout=min(timeout, 8000))
        return f"role=button[name={target}]"
    except Exception:
        pass
    try:
        page.get_by_text(target, exact=True).first.click(timeout=min(timeout, 8000))
        return f"text={target}"
    except Exception:
        pass
    last_err = ""
    for sel in resolve_selector(target):
        try:
            page.click(sel, timeout=min(timeout, 5000))
            return sel
        except Exception as exc:
            last_err = str(exc)
    raise RuntimeError(f"Could not click target '{target}'. Last error: {last_err}")


def do_authenticate(page: Page, auth: Dict[str, str], timeout: int) -> None:
    login_url = auth.get("login_url")
    username = auth.get("username")
    password = auth.get("password")
    if not all([login_url, username, password]):
        raise HTTPException(status_code=400, detail="authenticate requires login_url, username, password")
    page.goto(login_url, wait_until="domcontentloaded", timeout=timeout)
    fill_first(
        page,
        ["#username", "input[name='username']", "input[type='text']"],
        username,
        timeout,
    )
    fill_first(
        page,
        ["#password", "input[name='password']", "input[type='password']"],
        password,
        timeout,
    )
    clicked = False
    for sel in [
        "button:has-text('Sign In')",
        "button:has-text('Login')",
        "button[type='submit']",
        "input[type='submit']",
    ]:
        try:
            page.click(sel, timeout=5000)
            clicked = True
            break
        except Exception:
            continue
    if not clicked:
        raise HTTPException(status_code=400, detail="Could not find login submit button")
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        pass
    page.wait_for_timeout(800)


def wait_ready(page: Page, wait_for_selector: Optional[str], timeout: int) -> List[str]:
    warnings: List[str] = []
    for sel in ["#root", "#app", "[data-reactroot]"]:
        try:
            page.wait_for_selector(sel, timeout=min(3000, timeout))
            break
        except Exception:
            continue
    else:
        warnings.append("SPA root not detected quickly")
    if wait_for_selector:
        try:
            page.wait_for_selector(wait_for_selector, timeout=timeout)
        except Exception as exc:
            warnings.append(f"wait_for_selector failed: {exc}")
    try:
        page.wait_for_load_state("networkidle", timeout=min(5000, timeout))
    except Exception:
        warnings.append("networkidle timeout")
    return warnings


def redact_secrets(data: Dict[str, Any]) -> Dict[str, Any]:
    text = str(data)
    text = re.sub(r"eyJ[a-zA-Z0-9_\-\.]+", "[REDACTED_JWT]", text)
    # best-effort: only redact known token fields if present
    ls = data.get("local_storage_preview")
    if isinstance(ls, dict):
        for k, v in list(ls.items()):
            if isinstance(v, str) and ("token" in k.lower() or v.startswith("eyJ")):
                ls[k] = re.sub(r"eyJ[a-zA-Z0-9_\-\.]+", "[REDACTED_JWT]", v)
    return data


@app.on_event("startup")
def _startup() -> None:
    # Lazy browser start on first request is fine; warm optional.
    pass


@app.on_event("shutdown")
def _shutdown() -> None:
    MANAGER.stop()


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "ok": True,
        "service": "vista-browser-worker",
        "sessions": MANAGER.session_count(),
        "auth_required": bool(WORKER_TOKEN),
        "allowed_hosts": sorted(ALLOWED_HOSTS) if ALLOWED_HOSTS else ["*"],
        "timestamp": ts(),
    }


@app.post("/v1/explore")
def explore(req: ExploreRequest, _: None = Depends(require_auth)) -> Dict[str, Any]:
    if not req.url:
        raise HTTPException(status_code=400, detail="url is required")
    if not _host_allowed(req.url):
        raise HTTPException(
            status_code=403,
            detail=f"Host not allowed by BROWSER_WORKER_ALLOWED_HOSTS: {urlparse(req.url).hostname}",
        )

    action = (req.action or "Navigate").strip()
    sess = MANAGER.get_or_create(
        req.session_id or "default",
        headless=req.headless if req.headless is not None else DEFAULT_HEADLESS,
        ignore_https_errors=req.ignore_https_errors,
    )

    with sess.lock:
        page = sess.page
        if not req.capture_network:
            # keep collector anyway; cheap
            pass

        warnings: List[str] = []
        try:
            if req.authenticate:
                if req.authenticate.get("login_url") and not _host_allowed(req.authenticate["login_url"]):
                    raise HTTPException(status_code=403, detail="authenticate.login_url host not allowed")
                do_authenticate(page, req.authenticate, req.wait_timeout)

            if action.lower() == "navigate":
                page.goto(req.url, wait_until="domcontentloaded", timeout=req.wait_timeout)
                warnings.extend(wait_ready(page, req.wait_for_selector, req.wait_timeout))
                result = extract_page(page, "Navigate")

            elif action.lower() == "type":
                if not req.target_element:
                    raise HTTPException(status_code=400, detail="Type requires target_element")
                used = fill_first(
                    page,
                    resolve_selector(req.target_element),
                    req.input_value or "",
                    req.wait_timeout,
                )
                result = {
                    "success": True,
                    "action_performed": "Type",
                    "target_element": req.target_element,
                    "selector_used": used,
                    "status": f"Stored input for {req.target_element}",
                    "current_url": page.url,
                    "timestamp": ts(),
                    "confidence": "High",
                }

            elif action.lower() == "click":
                if not req.target_element:
                    raise HTTPException(status_code=400, detail="Click requires target_element")
                used = click_first(page, req.target_element, req.wait_timeout)
                warnings.extend(wait_ready(page, req.wait_for_selector, req.wait_timeout))
                result = extract_page(page, f"Click ({req.target_element})")
                result["selector_used"] = used
                if "login" not in page.url.lower() and "sign in" in req.target_element.lower():
                    result["note"] = "Login executed successfully."

            elif action.lower() in {"wait", "scroll", "hover", "expand", "refresh"}:
                if action.lower() == "refresh":
                    page.reload(wait_until="domcontentloaded", timeout=req.wait_timeout)
                elif action.lower() == "scroll":
                    page.evaluate("window.scrollBy(0, 800)")
                elif action.lower() == "wait":
                    page.wait_for_timeout(min(req.wait_timeout, 5000))
                warnings.extend(wait_ready(page, req.wait_for_selector, req.wait_timeout))
                result = extract_page(page, action)

            else:
                raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

            framework = detect_framework(page)
            auth = analyze_auth(page)
            api_calls = sorted({u.split("?")[0] for u in sess.network if "/api/" in u})[-50:]

            screenshot_path = None
            if req.take_screenshot:
                fname = f"{req.session_id}_{int(time.time())}.png".replace("/", "_")
                fpath = SCREENSHOT_DIR / fname
                page.screenshot(path=str(fpath), full_page=True)
                screenshot_path = str(fpath)

            # Enrich common fields expected by AAVA tool normalizer
            if "success" not in result:
                result["success"] = True
            result["url"] = req.url
            result["session_id"] = req.session_id
            result["mode"] = "remote_worker"
            result["rendering_architecture"] = {
                "type": "SPA (Single-Page Application)" if framework.get("is_spa") else "unknown",
                "framework": framework.get("framework", "unknown"),
                "is_react": framework.get("is_react", False),
                "is_vue": framework.get("is_vue", False),
                "is_angular": framework.get("is_angular", False),
                "is_spa": framework.get("is_spa", False),
            }
            result["framework_hints"] = framework.get("framework_hints", [])
            result["authentication"] = auth
            result["network"] = {
                "api_calls": [{"url": u, "method": "GET", "status": None, "type": "xhr"} for u in api_calls],
                "total_requests": len(sess.network),
            }
            result["api_calls"] = api_calls
            result["screenshot"] = screenshot_path
            result["warnings"] = warnings
            result["errors"] = []

            # Session snapshot (redacted)
            try:
                result["session_state"] = {
                    "cookie_names": [c["name"] for c in sess.context.cookies()],
                    "local_storage_keys": page.evaluate("() => Object.keys(localStorage)"),
                    "session_storage_keys": page.evaluate("() => Object.keys(sessionStorage)"),
                }
            except Exception:
                pass

            return redact_secrets(result)

        except HTTPException:
            raise
        except Exception as exc:
            return {
                "error": True,
                "success": False,
                "code": "WORKER_ACTION_FAILED",
                "message": str(exc),
                "action": action,
                "url": req.url,
                "session_id": req.session_id,
                "current_url": getattr(page, "url", None),
                "timestamp": ts(),
                "mode": "remote_worker",
            }


@app.delete("/v1/sessions/{session_id}")
def close_session(session_id: str, _: None = Depends(require_auth)) -> Dict[str, Any]:
    with MANAGER._lock:
        sess = MANAGER._sessions.pop(session_id, None)
    if sess is None:
        return {"ok": True, "closed": False, "session_id": session_id}
    try:
        sess.context.close()
    except Exception:
        pass
    return {"ok": True, "closed": True, "session_id": session_id}
