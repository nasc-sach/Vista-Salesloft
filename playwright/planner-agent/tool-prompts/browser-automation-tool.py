"""
BrowserAutomationTool - CrewAI tool that explores dynamic web apps via a remote Playwright worker.

AAVA Console / sandboxed CrewAI runtimes typically cannot install or launch Chromium.
This tool does NOT run Playwright in-process. It POSTs exploration requests to an
external Browser Worker that owns Playwright + Chromium, then returns structured JSON.

Architecture:
    AAVA CrewAI tool  --HTTP-->  Browser Worker (Playwright)  -->  target SPA

Environment:
    BROWSER_WORKER_URL      Base URL of the worker, e.g. https://browser-worker.example.com
    BROWSER_WORKER_TOKEN    Optional Bearer token for worker auth
    BROWSER_WORKER_TIMEOUT  Request timeout in seconds (default: 120)

Worker API (expected):
    POST {BROWSER_WORKER_URL}/v1/explore
    Authorization: Bearer <token>   (if configured)
    Body JSON:
      {
        "session_id": "planner-run-123",
        "url": "https://example.com",
        "action": "Navigate",          # Navigate | Type | Click | Wait | Scroll | Hover | Expand | Refresh
        "target_element": "",
        "input_value": "",
        "wait_for_selector": "#root",
        "wait_timeout": 30000,
        "capture_network": true,
        "take_screenshot": true,
        "headless": true,
        "authenticate": {"username": "...", "password": "...", "login_url": "..."},
        "ignore_https_errors": false
      }

Usage (AAVA / CrewAI):
    from browser_automation_tool import BrowserAutomationTool

    tool = BrowserAutomationTool()
    result = tool._run(
        url="https://vistapoc.nitor.in/login",
        session_id="run-1",
        action="Navigate",
        capture_network=True,
    )
"""

from __future__ import annotations

import json
import logging
import os
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional, Type
from urllib.parse import urlparse

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("BrowserAutomationTool")


class BrowserAutomationToolSchema(BaseModel):
    """Input schema for BrowserAutomationTool (remote worker client)."""

    url: str = Field(
        ...,
        description="Target application URL to explore with browser automation",
    )
    session_id: Optional[str] = Field(
        default="default",
        description=(
            "Worker browser-context session id. Reuse the same value across "
            "Navigate/Type/Click so login state (cookies/localStorage) is preserved."
        ),
    )
    action: Optional[str] = Field(
        default="Navigate",
        description=(
            "Browser action for the worker: Navigate, Type, Click, Wait, Scroll, "
            "Hover, Expand, Refresh. Defaults to Navigate."
        ),
    )
    target_element: Optional[str] = Field(
        default="",
        description="Element to interact with (selector, id, name, or visible text). Required for Click/Type.",
    )
    input_value: Optional[str] = Field(
        default="",
        description="Value to type into target_element. Required for Type.",
    )
    wait_for_selector: Optional[str] = Field(
        default=None,
        description="CSS selector to wait for before extraction (e.g., '#root', '.app-loaded')",
    )
    wait_timeout: int = Field(
        default=30000,
        description="Maximum wait time in milliseconds (default: 30000)",
    )
    capture_network: bool = Field(
        default=True,
        description="Capture network requests and API calls during page load",
    )
    take_screenshot: bool = Field(
        default=False,
        description="Ask worker to capture a screenshot (returned as path/URL from worker)",
    )
    headless: bool = Field(
        default=True,
        description="Run remote browser in headless mode (default: True)",
    )
    authenticate: Optional[Dict[str, str]] = Field(
        default=None,
        description=(
            "Optional login before exploration: "
            "{'username': '...', 'password': '...', 'login_url': '...'}"
        ),
    )
    ignore_https_errors: bool = Field(
        default=False,
        description="Ignore HTTPS/SSL certificate errors on the worker browser",
    )
    worker_url: Optional[str] = Field(
        default=None,
        description=(
            "Override BROWSER_WORKER_URL for this call. "
            "Prefer setting BROWSER_WORKER_URL in the environment."
        ),
    )


class BrowserAutomationTool(BaseTool):
    """
    Remote Playwright browser exploration tool for AAVA / CrewAI.

    Does not import or launch Playwright locally. Delegates to an external
    Browser Worker over HTTP so React/Vue/Angular SPAs can be explored from
    sandboxed runtimes that cannot install Chromium.
    """

    name: str = "Browser Automation Tool"
    description: str = (
        "Explore dynamic web applications (React/Vue/Angular SPAs) via a remote "
        "Playwright browser worker. Supports Navigate, Type, Click, auth login, "
        "network capture, and session reuse across tool calls. "
        "Requires BROWSER_WORKER_URL. Does not run Playwright inside AAVA."
    )
    args_schema: Type[BaseModel] = BrowserAutomationToolSchema

    USER_AGENT: ClassVar[str] = "Vista-Planner/1.0 (RemoteBrowserWorker)"
    DEFAULT_EXPLORE_PATH: ClassVar[str] = "/v1/explore"
    DEFAULT_TIMEOUT_SEC: ClassVar[int] = 120

    def _log(self, msg: str) -> None:
        logger.info("[%s] %s", self.name, msg)

    def _worker_base_url(self, override: Optional[str] = None) -> str:
        return (override or os.environ.get("BROWSER_WORKER_URL") or "").strip().rstrip("/")

    def _worker_token(self) -> str:
        return (os.environ.get("BROWSER_WORKER_TOKEN") or "").strip()

    def _worker_timeout(self) -> int:
        raw = os.environ.get("BROWSER_WORKER_TIMEOUT", str(self.DEFAULT_TIMEOUT_SEC))
        try:
            return max(5, int(raw))
        except ValueError:
            return self.DEFAULT_TIMEOUT_SEC

    def _error_payload(
        self,
        *,
        code: str,
        message: str,
        url: str = "",
        extra: Optional[Dict[str, Any]] = None,
    ) -> str:
        payload: Dict[str, Any] = {
            "error": True,
            "success": False,
            "code": code,
            "message": message,
            "tool": self.name,
            "url": url,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "mode": "remote_worker",
        }
        if extra:
            payload.update(extra)
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def _build_worker_payload(
        self,
        *,
        url: str,
        session_id: str,
        action: str,
        target_element: str,
        input_value: str,
        wait_for_selector: Optional[str],
        wait_timeout: int,
        capture_network: bool,
        take_screenshot: bool,
        headless: bool,
        authenticate: Optional[Dict[str, str]],
        ignore_https_errors: bool,
    ) -> Dict[str, Any]:
        return {
            "session_id": session_id or "default",
            "url": url,
            "action": (action or "Navigate").strip(),
            "target_element": target_element or "",
            "input_value": input_value or "",
            "wait_for_selector": wait_for_selector,
            "wait_timeout": wait_timeout,
            "capture_network": capture_network,
            "take_screenshot": take_screenshot,
            "headless": headless,
            "authenticate": authenticate,
            "ignore_https_errors": ignore_https_errors,
            "client": {
                "name": self.name,
                "user_agent": self.USER_AGENT,
            },
        }

    def _post_json(self, endpoint: str, payload: Dict[str, Any], timeout_sec: int) -> Dict[str, Any]:
        """POST JSON to the worker using stdlib urllib (AAVA-friendly)."""
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.USER_AGENT,
        }
        token = self._worker_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"

        request = urllib.request.Request(
            endpoint,
            data=body,
            headers=headers,
            method="POST",
        )

        # Workers may use self-signed certs in POC setups.
        context = ssl.create_default_context()
        if os.environ.get("BROWSER_WORKER_INSECURE_SSL", "").lower() in {"1", "true", "yes"}:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(request, timeout=timeout_sec, context=context) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status = getattr(resp, "status", 200)

        if not raw.strip():
            return {
                "error": True,
                "success": False,
                "code": "EMPTY_WORKER_RESPONSE",
                "message": f"Worker returned empty body (HTTP {status})",
                "http_status": status,
            }

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {
                "error": True,
                "success": False,
                "code": "INVALID_WORKER_JSON",
                "message": "Worker response was not valid JSON",
                "http_status": status,
                "raw_preview": raw[:500],
            }

        if isinstance(data, dict):
            data.setdefault("http_status", status)
            data.setdefault("mode", "remote_worker")
            return data

        return {
            "success": True,
            "mode": "remote_worker",
            "http_status": status,
            "result": data,
        }

    def _normalize_result(self, data: Dict[str, Any], request_url: str) -> Dict[str, Any]:
        """Ensure a stable shape for CrewAI agents even if the worker is minimal."""
        if data.get("error") and not data.get("success", True):
            data.setdefault("url", request_url)
            data.setdefault("mode", "remote_worker")
            return data

        data.setdefault("success", True)
        data.setdefault("url", request_url)
        data.setdefault("mode", "remote_worker")
        data.setdefault(
            "timestamp",
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        )

        # If worker returned Vista-style page evidence, also expose a compact summary.
        if "dom" not in data and any(
            k in data for k in ("input_fields", "buttons", "headings", "visible_text")
        ):
            data["dom"] = {
                "forms": data.get("forms", []),
                "inputs": data.get("input_fields", data.get("inputs", [])),
                "buttons": data.get("buttons", []),
                "links": data.get("all_links", data.get("links", [])),
                "headings": data.get("headings", []),
            }

        if "network" not in data and data.get("api_calls") is not None:
            data["network"] = {
                "api_calls": data.get("api_calls", []),
                "total_requests": data.get("total_requests", len(data.get("api_calls", []))),
            }

        if "recommendations" not in data:
            data["recommendations"] = self._generate_recommendations(data)

        return data

    def _generate_recommendations(self, data: Dict[str, Any]) -> List[str]:
        recs: List[str] = []
        rendering = data.get("rendering_architecture") or data.get("rendering") or {}
        auth = data.get("authentication") or {}
        network = data.get("network") or {}
        api_calls = network.get("api_calls") or data.get("api_calls") or []

        framework = rendering.get("framework") or ""
        framework_hints = data.get("framework_hints") or []
        if rendering.get("is_react") or "React" in framework or "React" in framework_hints:
            recs.append("React application detected via remote worker DOM inspection")
        if auth.get("has_login_form") or data.get("login_form_visible"):
            recs.append("Login form detected — reuse session_id after authenticate/Type+Click login")
        if api_calls:
            recs.append(f"Captured {len(api_calls)} API call(s) — review network.api_calls")
        if data.get("current_url"):
            recs.append(f"Worker current URL: {data['current_url']}")
        if not recs:
            recs.append("Remote worker exploration completed — inspect DOM/navigation fields")
        return recs

    def _run(
        self,
        url: str,
        session_id: Optional[str] = "default",
        action: Optional[str] = "Navigate",
        target_element: Optional[str] = "",
        input_value: Optional[str] = "",
        wait_for_selector: Optional[str] = None,
        wait_timeout: int = 30000,
        capture_network: bool = True,
        take_screenshot: bool = False,
        headless: bool = True,
        authenticate: Optional[Dict[str, str]] = None,
        ignore_https_errors: bool = False,
        worker_url: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Delegate browser exploration to the remote Playwright worker.

        Returns:
            JSON string with exploration results for CrewAI agent consumption.
        """
        base = self._worker_base_url(worker_url)
        if not base:
            return self._error_payload(
                code="WORKER_URL_NOT_CONFIGURED",
                message=(
                    "BROWSER_WORKER_URL is not set. This tool does not run Playwright "
                    "inside AAVA. Deploy a Playwright browser worker and set "
                    "BROWSER_WORKER_URL (and optionally BROWSER_WORKER_TOKEN)."
                ),
                url=url,
                extra={
                    "hint": (
                        "Worker should expose POST /v1/explore and keep browser "
                        "contexts keyed by session_id for login persistence."
                    ),
                    "required_env": ["BROWSER_WORKER_URL"],
                    "optional_env": [
                        "BROWSER_WORKER_TOKEN",
                        "BROWSER_WORKER_TIMEOUT",
                        "BROWSER_WORKER_INSECURE_SSL",
                    ],
                },
            )

        parsed = urlparse(base)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return self._error_payload(
                code="INVALID_WORKER_URL",
                message=f"Invalid BROWSER_WORKER_URL: {base}",
                url=url,
            )

        action_str = (action or "Navigate").strip()
        if action_str.lower() in {"type", "click"} and not (target_element or "").strip():
            return self._error_payload(
                code="MISSING_TARGET_ELEMENT",
                message=f"action={action_str} requires target_element",
                url=url,
            )
        if action_str.lower() == "type" and input_value is None:
            return self._error_payload(
                code="MISSING_INPUT_VALUE",
                message="action=Type requires input_value",
                url=url,
            )

        endpoint = base + self.DEFAULT_EXPLORE_PATH

        payload = self._build_worker_payload(
            url=url,
            session_id=session_id or "default",
            action=action_str,
            target_element=target_element or "",
            input_value=input_value or "",
            wait_for_selector=wait_for_selector,
            wait_timeout=wait_timeout,
            capture_network=capture_network,
            take_screenshot=take_screenshot,
            headless=headless,
            authenticate=authenticate,
            ignore_https_errors=ignore_https_errors,
        )

        # Allow passthrough of unknown kwargs to worker for forward compatibility.
        for key, value in kwargs.items():
            if key not in payload and value is not None:
                payload[key] = value

        timeout_sec = self._worker_timeout()
        self._log(
            f"Delegating to worker action={action_str} session={payload['session_id']} "
            f"url={url} endpoint={endpoint}"
        )

        try:
            result = self._post_json(endpoint, payload, timeout_sec)
            result = self._normalize_result(result, url)
            return json.dumps(result, ensure_ascii=False, indent=2)

        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")
            except Exception:
                body = ""
            detail: Any
            try:
                detail = json.loads(body) if body else body
            except json.JSONDecodeError:
                detail = body[:1000]
            return self._error_payload(
                code="WORKER_HTTP_ERROR",
                message=f"Worker returned HTTP {exc.code}: {exc.reason}",
                url=url,
                extra={"http_status": exc.code, "worker_detail": detail, "endpoint": endpoint},
            )

        except urllib.error.URLError as exc:
            return self._error_payload(
                code="WORKER_UNREACHABLE",
                message=(
                    f"Could not reach browser worker at {endpoint}. "
                    f"Reason: {exc.reason}. Ensure the worker is running and "
                    "reachable from AAVA (public URL, VPN, or tunnel)."
                ),
                url=url,
                extra={"endpoint": endpoint, "reason": str(exc.reason)},
            )

        except TimeoutError:
            return self._error_payload(
                code="WORKER_TIMEOUT",
                message=f"Worker request timed out after {timeout_sec}s",
                url=url,
                extra={"endpoint": endpoint, "timeout_sec": timeout_sec},
            )

        except Exception as exc:
            self._log(f"Unexpected client error: {exc}")
            return self._error_payload(
                code="BROWSER_AUTOMATION_ERROR",
                message=str(exc),
                url=url,
                extra={"endpoint": endpoint},
            )


__all__ = ["BrowserAutomationTool", "BrowserAutomationToolSchema"]
