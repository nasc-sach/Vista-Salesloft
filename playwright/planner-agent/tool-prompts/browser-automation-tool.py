"""
BrowserAutomationTool - CrewAI tool for dynamic web application exploration using Playwright.

This tool handles React.js SPAs and dynamic content that require JavaScript execution.
It complements BrowserExplorer (static HTML parsing) with full browser automation.

Installation:
    pip install playwright
    playwright install chromium

Usage:
    from browser_automation_tool import BrowserAutomationTool
    
    tool = BrowserAutomationTool()
    result = tool._run(
        url="https://example.com",
        wait_for_selector="#root",
        capture_network=True,
        take_screenshot=True
    )
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
from urllib.parse import urljoin, urlparse
import subprocess

from pydantic import BaseModel, Field
from crewai.tools import BaseTool

try:
    from playwright.async_api import async_playwright, Browser, Page, Response
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BrowserAutomationToolSchema(BaseModel):
    """Input schema for BrowserAutomationTool."""
    
    url: str = Field(
        ...,
        description="Target application URL to explore with browser automation"
    )
    wait_for_selector: Optional[str] = Field(
        default=None,
        description="CSS selector to wait for before extraction (e.g., '#root', '.app-loaded')"
    )
    wait_timeout: int = Field(
        default=30000,
        description="Maximum wait time in milliseconds (default: 30000)"
    )
    capture_network: bool = Field(
        default=True,
        description="Capture network requests and API calls during page load"
    )
    take_screenshot: bool = Field(
        default=True,
        description="Take screenshot for debugging (saved to screenshots/ directory)"
    )
    headless: bool = Field(
        default=True,
        description="Run browser in headless mode (default: True)"
    )
    authenticate: Optional[Dict[str, str]] = Field(
        default=None,
        description="Authentication credentials: {'username': '...', 'password': '...', 'login_url': '...'}"
    )
    ignore_https_errors: bool = Field(
        default=False,
        description="Ignore HTTPS/SSL certificate errors (for self-signed certificates)"
    )


class BrowserAutomationTool(BaseTool):
    """
    Browser automation tool using Playwright for dynamic web application exploration.
    
    **Capabilities:**
    - Execute JavaScript and wait for React/Vue/Angular hydration
    - Extract fully-rendered DOM after dynamic content loads
    - Detect SPA frameworks (React, Vue, Angular) via runtime inspection
    - Capture network traffic (XHR/Fetch API calls)
    - Handle authentication flows and session management
    - Take screenshots for debugging
    - Analyze React Router routes and component structure
    
    **Use Cases:**
    - React.js SPAs that render content client-side
    - Applications with dynamic forms/inputs loaded via JavaScript
    - API endpoint discovery through network traffic analysis
    - Authentication flow testing
    - Post-login page exploration
    
    **Output:**
    Returns structured JSON with:
    - Rendering architecture (SPA/SSR/MPA)
    - Framework detection (React/Vue/Angular)
    - Fully-rendered DOM elements (forms, inputs, navigation)
    - Network requests (API calls, endpoints)
    - Authentication analysis
    - Screenshots and recommendations
    """
    
    name: str = "Browser Automation Tool"
    description: str = """
    Advanced browser automation tool for exploring dynamic web applications.
    Uses Playwright to execute JavaScript and extract fully-rendered content.
    Ideal for React SPAs, authentication flows, and network traffic analysis.
    """
    args_schema: Type[BaseModel] = BrowserAutomationToolSchema
    
    # Class constants
    USER_AGENT = "Vista-Planner/1.0 (Playwright)"
    SCREENSHOT_DIR = Path("screenshots")
    REACT_SELECTORS = ["#root", "#app", "[data-reactroot]", "[data-reactid]"]
    VUE_SELECTORS = ["#app", "[data-v-]", "[data-app]"]
    ANGULAR_SELECTORS = ["[ng-version]", "app-root", "[ng-app]"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.SCREENSHOT_DIR.mkdir(exist_ok=True)
        
        if not PLAYWRIGHT_AVAILABLE:
            logging.warning(
                "[BrowserAutomationTool] Playwright not installed. "
                "Install with: pip install playwright && playwright install chromium"
            )
    
    def _log(self, msg: str) -> None:
        """Log message with tool name prefix."""
        logging.info(f"[{self.name}] {msg}")
    
    async def _check_browser_installed(self) -> bool:
        """Check if Chromium browser is installed at runtime."""
        try:
            result = subprocess.run(
                ["playwright", "show-browser"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 or "chromium" in result.stdout.lower()
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            # If command fails, assume browser not installed
            return False
    
    def _run(
        self,
        url: str,
        wait_for_selector: Optional[str] = None,
        wait_timeout: int = 30000,
        capture_network: bool = True,
        take_screenshot: bool = True,
        headless: bool = True,
        authenticate: Optional[Dict[str, str]] = None,
        ignore_https_errors: bool = False,
        **kwargs
    ) -> str:
        """
        Main execution method - runs async browser automation synchronously.
        
        Returns:
            JSON string with exploration results for CrewAI agent consumption
        """
        if not PLAYWRIGHT_AVAILABLE:
            return json.dumps({
                "error": True,
                "code": "PLAYWRIGHT_NOT_INSTALLED",
                "message": (
                    "Playwright is not installed. "
                    "Install with: pip install playwright && playwright install chromium"
                ),
                "tool": self.name,
                "url": url
            }, indent=2)
        
        try:
            # Run async automation in sync context
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If event loop is already running, create new one
                import nest_asyncio
                nest_asyncio.apply()
            
            result = asyncio.run(
                self._run_automation(
                    url=url,
                    wait_for_selector=wait_for_selector,
                    wait_timeout=wait_timeout,
                    capture_network=capture_network,
                    take_screenshot=take_screenshot,
                    headless=headless,
                    authenticate=authenticate,
                    ignore_https_errors=ignore_https_errors
                )
            )
            
            return json.dumps(result, indent=2)
            
        except Exception as exc:
            self._log(f"Error during browser automation: {exc}")
            return json.dumps({
                "error": True,
                "code": "BROWSER_AUTOMATION_ERROR",
                "message": str(exc),
                "tool": self.name,
                "url": url
            }, indent=2)
    
    async def _run_automation(
        self,
        url: str,
        wait_for_selector: Optional[str],
        wait_timeout: int,
        capture_network: bool,
        take_screenshot: bool,
        headless: bool,

        authenticate: Optional[Dict[str, str]],
        ignore_https_errors: bool = False
    ) -> Dict[str, Any]:
        """
        Async browser automation workflow.
        
        Returns:
            Dictionary with structured exploration results
        """
        start_time = time.time()
        self._log(f"Starting browser automation for: {url}")
        
        # Network capture storage
        network_requests: List[Dict[str, Any]] = []
        api_calls: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        warnings: List[str] = []
        
        # Check browser installation before launching
        if not await self._check_browser_installed():
            return {
                "error": True,
                "success": False,
                "code": "CHROMIUM_NOT_INSTALLED",
                "message": (
                    "Chromium browser not found. Install with:\n"
                    "  playwright install chromium"
                ),
                "url": url,
                "errors": [{
                    "stage": "browser_check",
                    "error": "Chromium binary not installed",
                    "type": "InstallationError"
                }],
                "warnings": []
            }
        
        async with async_playwright() as p:

            # Wrap browser launch in try/except
            try:
                browser = await p.chromium.launch(headless=headless)
            except Exception as launch_exc:
                error_msg = str(launch_exc)
                if "Executable doesn't exist" in error_msg or "Failed to launch" in error_msg:
                    code = "CHROMIUM_NOT_FOUND"
                    message = (
                        "Failed to launch Chromium browser. Install with:\n"
                        "  playwright install chromium"
                    )
                else:
                    code = "BROWSER_LAUNCH_FAILED"
                    message = f"Browser launch failed: {error_msg}"
                
                return {
                    "error": True,
                    "success": False,
                    "code": code,
                    "message": message,
                    "url": url,
                    "errors": [{"stage": "browser_launch", "error": error_msg, "type": type(launch_exc).__name__}],
                    "warnings": []
                }
            
            try:
                context = await browser.new_context(
                    user_agent=self.USER_AGENT,
                    viewport={"width": 1920, "height": 1080},
                    ignore_https_errors=ignore_https_errors
                )

                
                page = await context.new_page()
                
                # Setup network capture
                if capture_network:
                    page.on("response", lambda response: self._capture_response(
                        response, network_requests, api_calls
                    ))
                
                # Handle authentication if provided
                if authenticate:
                    await self._handle_authentication(page, authenticate, wait_timeout)
                
                # Navigate to target URL
                self._log(f"Navigating to: {url}")
                navigation_start = time.time()
                
                # Navigate with proper error handling
                try:
                    response = await page.goto(url, wait_until="domcontentloaded", timeout=wait_timeout)
                    
                    # Check response status
                    if response:
                        status = response.status
                        if status >= 400:
                            warnings.append(f"HTTP {status} response from server")
                            if status >= 500:
                                errors.append({
                                    "stage": "navigation",
                                    "error": f"Server error: HTTP {status}",
                                    "type": "HTTPError",
                                    "status_code": status
                                })
                    
                except Exception as nav_exc:
                    error_msg = str(nav_exc)
                    error_type = type(nav_exc).__name__
                    
                    # Categorize navigation errors
                    if "net::ERR_CERT" in error_msg or "SSL" in error_msg or "certificate" in error_msg.lower():
                        code = "SSL_ERROR"
                        message = (
                            f"SSL certificate error: {error_msg}\n"
                            "Retry with ignore_https_errors=True for self-signed certificates."
                        )
                    elif "net::ERR_NAME_NOT_RESOLVED" in error_msg or "DNS" in error_msg:
                        code = "DNS_ERROR"
                        message = f"DNS resolution failed: {error_msg}"
                    elif "Timeout" in error_type or "timeout" in error_msg.lower():
                        code = "TIMEOUT_ERROR"
                        message = f"Navigation timeout ({wait_timeout}ms): {error_msg}"
                    elif "net::ERR_CONNECTION" in error_msg:
                        code = "CONNECTION_ERROR"
                        message = f"Connection failed: {error_msg}"
                    else:
                        code = "NAVIGATION_ERROR"
                        message = f"Navigation failed: {error_msg}"
                    
                    self._log(f"❌ {message}")
                    
                    # Abort on critical navigation error
                    errors.append({
                        "stage": "navigation",
                        "error": error_msg,
                        "type": error_type,
                        "code": code
                    })
                    
                    return {
                        "error": True,
                        "success": False,
                        "code": code,
                        "message": message,
                        "url": url,
                        "errors": errors,
                        "warnings": warnings
                    }
                
                # Wait for network idle (React hydration)
                try:
                    # Longer timeout for React hydration
                    react_timeout = wait_timeout * 2
                    await page.wait_for_load_state("networkidle", timeout=react_timeout)
                except Exception as e:
                    warnings.append(f"Network idle timeout after {react_timeout}ms (may indicate slow React hydration)")
                    self._log(f"⚠ Network idle timeout (expected for some SPAs): {e}")
                
                # Wait for specific selector if provided
                if wait_for_selector:
                    self._log(f"Waiting for selector: {wait_for_selector}")
                    try:
                        await page.wait_for_selector(wait_for_selector, timeout=wait_timeout)
                    except Exception as sel_exc:
                        warnings.append(f"Selector '{wait_for_selector}' not found within {wait_timeout}ms")
                        self._log(f"⚠ Selector timeout: {sel_exc}")
                else:
                    # Auto-detect framework and wait for common root elements
                    framework_found = await self._wait_for_framework_root(page, wait_timeout)
                    if not framework_found:
                        warnings.append("No React/Vue/Angular root element detected within timeout")

                navigation_time = (time.time() - navigation_start) * 1000
                self._log(f"Page loaded in {navigation_time:.0f}ms")
                
                # Extract data after hydration
                rendering = await self._detect_rendering_architecture(page, url)
                dom_data = await self._extract_dom_data(page, url)
                auth_data = await self._analyze_authentication(page)
                
                # Take screenshot
                screenshot_path = None
                if take_screenshot:
                    screenshot_path = await self._take_screenshot(page, url)
                
                # Generate recommendations
                recommendations = self._generate_recommendations(
                    rendering, dom_data, auth_data, api_calls
                )
                
                execution_time = (time.time() - start_time) * 1000
                
                result = {
                    "url": url,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "execution_time_ms": round(execution_time, 2),
                    "rendering": {
                        **rendering,
                        "hydration_time_ms": round(navigation_time, 2)
                    },
                    "dom": dom_data,
                    "network": {
                        "total_requests": len(network_requests),
                        "api_calls": api_calls,
                        "resource_summary": self._summarize_resources(network_requests)
                    },
                    "authentication": auth_data,
                    "screenshot_path": screenshot_path,
                    "recommendations": recommendations
                }
                












                result = {
                    "url": url,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "execution_time_ms": round(execution_time, 2),
                    "success": len(errors) == 0,
                    "rendering": {
                        **rendering,
                        "hydration_time_ms": round(navigation_time, 2)
                    },
                    "dom": dom_data,
                    "network": {
                        "total_requests": len(network_requests),
                        "api_calls": api_calls,
                        "resource_summary": self._summarize_resources(network_requests)
                    },
                    "authentication": auth_data,
                    "screenshot_path": screenshot_path,
                    "recommendations": recommendations,
                    "errors": errors,
                    "warnings": warnings
                }
                
                self._log(f"Automation completed in {execution_time:.0f}ms")
                return result
                
            finally:
                await browser.close()
    
    def _capture_response(
        self,
        response: Response,
        network_requests: List[Dict[str, Any]],
        api_calls: List[Dict[str, Any]]
    ) -> None:

        """Capture network response (sync callback)."""
        try:
            url = response.url
            method = response.request.method
            status = response.status
            content_type = response.headers.get("content-type", "")
            
            request_data = {
                "url": url,
                "method": method,
                "status": status,
                "content_type": content_type
            }
            
            network_requests.append(request_data)
            
            # Identify API calls (JSON responses, common API patterns)
            if any([
                "application/json" in content_type,
                "/api/" in url,
                "/graphql" in url,
                method in ["POST", "PUT", "PATCH", "DELETE"]
            ]):
                api_calls.append({
                    "endpoint": url,
                    "method": method,
                    "status": status,
                    "content_type": content_type
                })
        except Exception as e:
            self._log(f"Error capturing response: {e}")
    
    async def _handle_authentication(
        self,
        page: Page,
        auth_config: Dict[str, str],
        timeout: int
    ) -> None:
        """Handle authentication flow before navigating to target URL."""
        login_url = auth_config.get("login_url")
        username = auth_config.get("username")
        password = auth_config.get("password")
        
        if not all([login_url, username, password]):
            self._log("Incomplete authentication config - skipping login")
            return
        
        try:
            self._log(f"Attempting authentication at: {login_url}")
            await page.goto(login_url, wait_until="domcontentloaded", timeout=timeout)
            
            # Common username field selectors
            username_selectors = [
                'input[name="username"]',
                'input[name="email"]',
                'input[type="email"]',
                'input[id="username"]',
                'input[id="email"]',
                '#username',
                '#email'
            ]
            
            # Common password field selectors
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                '#password'
            ]
            
            # Find and fill username
            for selector in username_selectors:
                try:
                    await page.fill(selector, username, timeout=5000)
                    self._log(f"Filled username field: {selector}")
                    break
                except Exception:
                    continue
            
            # Find and fill password
            for selector in password_selectors:
                try:
                    await page.fill(selector, password, timeout=5000)
                    self._log(f"Filled password field: {selector}")
                    break
                except Exception:
                    continue
            
            # Submit form (find submit button)
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Sign in")',
                'button:has-text("Login")'
            ]
            
            for selector in submit_selectors:
                try:
                    await page.click(selector, timeout=5000)
                    self._log(f"Clicked submit button: {selector}")
                    break
                except Exception:
                    continue
            
            # Wait for navigation after login
            await page.wait_for_load_state("networkidle", timeout=timeout)
            self._log("Authentication completed")
            
        except Exception as e:
            self._log(f"Authentication failed: {e}")
    
    async def _wait_for_framework_root(self, page: Page, timeout: int) -> bool:
        """Wait for common framework root elements to appear. Returns True if found."""













        all_selectors = (
            self.REACT_SELECTORS +
            self.VUE_SELECTORS +
            self.ANGULAR_SELECTORS
        )
        
        # Try to wait for any common root selector with retry logic
        for selector in all_selectors:
            try:
                # Longer timeout for each React selector attempt
                await page.wait_for_selector(selector, timeout=8000)
                self._log(f"Found framework root: {selector}")
                return True
            except Exception:
                continue
        
        # If no framework root found, wait a bit for dynamic content
        self._log("No framework root element detected")
        await page.wait_for_timeout(2000)
        return False

    
    async def _detect_rendering_architecture(
        self,
        page: Page,
        url: str
    ) -> Dict[str, Any]:
        """
        Detect rendering architecture and framework using runtime inspection.
        
        Returns:
            Dictionary with architecture, framework, and evidence
        """
        self._log("Detecting rendering architecture...")
        
        evidence = []
        framework = "Unknown"
        architecture = "Unknown"
        
        # Check for React
        react_detected = await page.evaluate("""
            () => {
                return !!(
                    window.React ||
                    document.querySelector('[data-reactroot]') ||
                    document.querySelector('[data-reactid]') ||
                    Array.from(document.querySelectorAll('*')).some(el => {
                        return Object.keys(el).some(key => key.startsWith('__react'));
                    })
                );
            }
        """)
        
        if react_detected:
            framework = "React"
            evidence.append("React runtime detected via window.React or React fiber")
        
        # Check for Vue
        vue_detected = await page.evaluate("""
            () => {
                return !!(
                    window.Vue ||
                    document.querySelector('[data-v-]') ||
                    document.querySelector('[data-app]') ||
                    Array.from(document.querySelectorAll('*')).some(el => {
                        return el.__vue__ || el.__vueParentComponent;
                    })
                );
            }
        """)
        
        if vue_detected:
            framework = "Vue"
            evidence.append("Vue runtime detected via window.Vue or Vue directives")
        
        # Check for Angular
        angular_detected = await page.evaluate("""
            () => {
                return !!(
                    window.ng ||
                    window.angular ||
                    document.querySelector('[ng-version]') ||
                    document.querySelector('app-root')
                );
            }
        """)
        
        if angular_detected:
            framework = "Angular"
            evidence.append("Angular runtime detected via ng-version or app-root")
        
        # Determine architecture (SPA vs SSR vs MPA)
        # Check if initial HTML was empty (SPA) or pre-rendered (SSR)
        initial_html = await page.evaluate("() => document.documentElement.outerHTML")
        
        # Simple heuristic: SSR has significant content in initial HTML
        body_content = await page.evaluate("() => document.body.innerText")
        content_length = len(body_content.strip())
        
        if content_length < 100:
            architecture = "SPA"
            evidence.append(f"Minimal initial content ({content_length} chars) - likely client-side rendered")
        elif content_length > 500:
            if framework != "Unknown":
                architecture = "SSR"
                evidence.append(f"Substantial initial content ({content_length} chars) with framework - likely SSR")
            else:
                architecture = "MPA"
                evidence.append(f"Substantial content without framework - traditional MPA")
        else:
            architecture = "Hybrid"
            evidence.append(f"Moderate content ({content_length} chars) - hybrid rendering")
        
        return {
            "architecture": architecture,
            "framework": framework,
            "evidence": evidence
        }
    
    async def _extract_dom_data(self, page: Page, base_url: str) -> Dict[str, Any]:
        """
        Extract structured data from fully-rendered DOM.
        
        Returns:
            Dictionary with title, forms, inputs, navigation, etc.
        """
        self._log("Extracting DOM data...")
        
        # Extract page title
        title = await page.title()
        
        # Extract forms
        forms = await page.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('form')).map(form => ({
                    action: form.action || '',
                    method: form.method || 'GET',
                    id: form.id || null,
                    inputs: Array.from(form.querySelectorAll('input, textarea, select')).map(input => ({
                        name: input.name || null,
                        type: input.type || 'text',
                        id: input.id || null,
                        placeholder: input.placeholder || null,
                        required: input.required || false
                    }))
                }));
            }
        """)
        
        # Extract all interactive elements
        interactive_elements = await page.evaluate("""
            () => {
                const buttons = Array.from(document.querySelectorAll('button, [role="button"]')).map(btn => ({
                    type: 'button',
                    text: btn.innerText.trim().substring(0, 100),
                    id: btn.id || null,
                    class: btn.className || null
                }));
                
                const links = Array.from(document.querySelectorAll('a[href]')).map(a => ({
                    type: 'link',
                    href: a.href,
                    text: a.innerText.trim().substring(0, 100)
                }));
                
                return {
                    buttons: buttons.slice(0, 50),  // Limit to first 50
                    links: links.slice(0, 50)
                };
            }
        """)
        
        # Extract navigation structure
        navigation = await self._extract_navigation(page, base_url)
        
        # Extract meta information
        meta = await page.evaluate("""
            () => {
                const metas = Array.from(document.querySelectorAll('meta'));
                return {
                    description: document.querySelector('meta[name="description"]')?.content || null,
                    keywords: document.querySelector('meta[name="keywords"]')?.content || null,
                    viewport: document.querySelector('meta[name="viewport"]')?.content || null,
                    charset: document.characterSet || null
                };
            }
        """)
        
        return {
            "title": title,
            "meta": meta,
            "forms": forms,
            "interactive_elements": interactive_elements,
            "navigation": navigation
        }
    
    async def _extract_navigation(self, page: Page, base_url: str) -> Dict[str, Any]:
        """Extract navigation structure from page."""
        nav_elements = await page.evaluate("""
            () => {
                const navs = Array.from(document.querySelectorAll('nav, [role="navigation"]'));
                return navs.map(nav => {
                    const links = Array.from(nav.querySelectorAll('a[href]')).map(a => ({
                        href: a.href,
                        text: a.innerText.trim()
                    }));
                    return {
                        id: nav.id || null,
                        class: nav.className || null,
                        links: links
                    };
                });
            }
        """)
        
        # Categorize links
        internal_links = []
        external_links = []
        
        for nav in nav_elements:
            for link in nav.get("links", []):
                href = link.get("href", "")
                parsed_base = urlparse(base_url)
                parsed_href = urlparse(href)
                
                if parsed_href.netloc == "" or parsed_href.netloc == parsed_base.netloc:
                    internal_links.append(link)
                else:
                    external_links.append(link)
        
        return {
            "nav_elements": nav_elements,
            "internal_links": internal_links[:30],  # Limit for JSON size
            "external_links": external_links[:10]
        }
    
    async def _analyze_authentication(self, page: Page) -> Dict[str, Any]:
        """Analyze page for authentication indicators."""
        self._log("Analyzing authentication...")
        
        # Check for common authentication indicators
        auth_indicators = await page.evaluate("""
            () => {
                const loginForm = document.querySelector('form[action*="login"], form[action*="signin"], form#login, form#signin');
                const loginButton = document.querySelector('button:has-text("Log in"), button:has-text("Sign in"), a:has-text("Log in"), a:has-text("Sign in")');
                const logoutButton = document.querySelector('button:has-text("Log out"), button:has-text("Sign out"), a:has-text("Log out"), a:has-text("Sign out")');
                const passwordField = document.querySelector('input[type="password"]');
                const userMenu = document.querySelector('[aria-label*="user"], [data-testid*="user"]');
                
                return {
                    hasLoginForm: !!loginForm,
                    hasLoginButton: !!loginButton,
                    hasLogoutButton: !!logoutButton,
                    hasPasswordField: !!passwordField,
                    hasUserMenu: !!userMenu
                };
            }
        """)
        
        # Determine authentication state
        detected = any([
            auth_indicators["hasLoginForm"],
            auth_indicators["hasLoginButton"],
            auth_indicators["hasLogoutButton"],
            auth_indicators["hasPasswordField"]
        ])
        
        # Check if user appears to be logged in
        logged_in = auth_indicators["hasLogoutButton"] or auth_indicators["hasUserMenu"]
        
        evidence = []
        if auth_indicators["hasLoginForm"]:
            evidence.append("Login form detected on page")
        if auth_indicators["hasPasswordField"]:
            evidence.append("Password input field found")
        if auth_indicators["hasLogoutButton"]:
            evidence.append("Logout button detected - user appears logged in")
        if auth_indicators["hasUserMenu"]:
            evidence.append("User menu detected - user appears logged in")
        
        return {
            "detected": detected,
            "login_form_present": auth_indicators["hasLoginForm"],
            "logged_in": logged_in,
            "evidence": evidence
        }
    
    async def _take_screenshot(self, page: Page, url: str) -> str:
        """Take screenshot and save to screenshots directory."""
        try:
            # Generate filename from URL and timestamp
            parsed = urlparse(url)
            domain = parsed.netloc.replace(".", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{domain}_{timestamp}.png"
            filepath = self.SCREENSHOT_DIR / filename
            
            await page.screenshot(path=str(filepath), full_page=True)
            self._log(f"Screenshot saved: {filepath}")
            
            return str(filepath)
        except Exception as e:
            self._log(f"Failed to take screenshot: {e}")
            return None
    
    def _summarize_resources(self, network_requests: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize network requests by resource type."""
        summary = {
            "document": 0,
            "stylesheet": 0,
            "image": 0,
            "script": 0,
            "xhr": 0,
            "fetch": 0,
            "other": 0
        }
        
        for req in network_requests:
            content_type = req.get("content_type", "").lower()
            
            if "text/html" in content_type:
                summary["document"] += 1
            elif "text/css" in content_type or "stylesheet" in content_type:
                summary["stylesheet"] += 1
            elif "image/" in content_type:
                summary["image"] += 1
            elif "javascript" in content_type or "ecmascript" in content_type:
                summary["script"] += 1
            elif "application/json" in content_type:
                if req.get("method") == "GET":
                    summary["xhr"] += 1
                else:
                    summary["fetch"] += 1
            else:
                summary["other"] += 1
        
        return summary
    
    def _generate_recommendations(
        self,
        rendering: Dict[str, Any],
        dom_data: Dict[str, Any],
        auth_data: Dict[str, Any],
        api_calls: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Architecture recommendations
        if rendering["architecture"] == "SPA":
            recommendations.append(
                "[INFO] SPA architecture detected. Full DOM rendered successfully with browser automation."
            )
        elif rendering["architecture"] == "SSR":
            recommendations.append(
                "[INFO] SSR architecture detected. Content is pre-rendered, both static and dynamic analysis possible."
            )
        
        # Framework-specific recommendations
        framework = rendering["framework"]
        if framework == "React":
            recommendations.append(
                "[FRAMEWORK] React application detected. Consider analyzing React Router routes and component tree."
            )
        elif framework == "Vue":
            recommendations.append(
                "[FRAMEWORK] Vue application detected. Consider analyzing Vue Router configuration."
            )
        elif framework == "Angular":
            recommendations.append(
                "[FRAMEWORK] Angular application detected. Consider analyzing routing module and services."
            )
        
        # Authentication recommendations
        if auth_data["detected"]:
            if auth_data["logged_in"]:
                recommendations.append(
                    "[AUTH] User appears to be logged in. Explore authenticated sections of the application."
                )
            else:
                recommendations.append(
                    "[AUTH] Login form detected. Consider using authenticate parameter to explore protected areas."
                )
        
        # API endpoint recommendations
        if api_calls:
            unique_endpoints = set(call["endpoint"] for call in api_calls)
            recommendations.append(
                f"[API] Captured {len(api_calls)} API calls to {len(unique_endpoints)} unique endpoints. "
                "Review network.api_calls for details."
            )
        
        # Form recommendations
        forms = dom_data.get("forms", [])
        if forms:
            recommendations.append(
                f"[FORMS] Detected {len(forms)} forms on page. Review dom.forms for input fields and actions."
            )
        
        # Navigation recommendations
        nav_data = dom_data.get("navigation", {})
        internal_links = nav_data.get("internal_links", [])
        if len(internal_links) > 10:
            recommendations.append(
                f"[NAVIGATION] Found {len(internal_links)} internal links. Consider crawling for full site map."
            )
        
        return recommendations


# Export tool class for CrewAI integration
__all__ = ["BrowserAutomationTool", "BrowserAutomationToolSchema"]