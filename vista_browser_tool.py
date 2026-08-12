"""
Vista Browser Exploration Tool - Simulated browser for AAVA Console training/testing.

A synchronous CrewAI tool that simulates browser interactions with pre-defined pages.
Uses urllib for HTTP requests (no Playwright dependency) and maintains session state
for login flows, form interactions, and navigation.

Key Features:
- Simulates Navigate, Type, Click, Wait, Scroll, Hover, Expand, Refresh actions
- Pre-defined PAGES dictionary with LOGIN, DASHBOARD, ADMIN, PIM, LEAVE responses
- Session state management (URL, form fields, login status)
- JSON response structure for CrewAI agent consumption
- No async dependencies (synchronous _run method)

Usage:
    from vista_browser_tool import VistaBrowserTool
    
    tool = VistaBrowserTool()
    
    # Navigate to login page
    result = tool._run(action="Navigate", url="https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
    
    # Type credentials
    tool._run(action="Type", selector="input[name='username']", text="Admin")
    tool._run(action="Type", selector="input[name='password']", text="admin123")
    
    # Click login button
    result = tool._run(action="Click", selector="button[type='submit']")
    
    # Navigate to PIM module
    result = tool._run(action="Navigate", url="https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList")
"""

import json
import logging
import ssl
import time
from datetime import datetime
from typing import Any, Dict, Optional, Type
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ============================================================================
# MODULE-LEVEL STATE (private naming convention with underscore prefix)
# ============================================================================

_STATE: Dict[str, Any] = {
    "current_url": None,
    "fields": {},  # Stores typed form field values
    "loggedin": False,
    "session_start": None,
    "action_count": 0
}

_SSL_CONTEXT = ssl.create_default_context()
_SSL_CONTEXT.check_hostname = False
_SSL_CONTEXT.verify_mode = ssl.CERT_NONE

_COOKIE_JAR = HTTPCookieProcessor()
_OPENER = build_opener(_COOKIE_JAR)

# ============================================================================
# PRE-DEFINED PAGES DICTIONARY
# ============================================================================

PAGES = {
    "LOGIN": {
        "current_url": "https://opensource-demo.orangehrmlive.com/web/index.php/auth/login",
        "page_title": "OrangeHRM",
        "https": True,
        "headings": ["Login"],
        "input_fields": [
            {
                "type": "text",
                "name": "username",
                "id": "txtUsername",
                "placeholder": "Username",
                "required": True,
                "aria_label": "Username"
            },
            {
                "type": "password",
                "name": "password",
                "id": "txtPassword",
                "placeholder": "Password",
                "required": True,
                "aria_label": "Password"
            }
        ],
        "buttons": [
            {
                "type": "submit",
                "text": "Login",
                "id": "btnLogin",
                "class": "oxd-button oxd-button--medium oxd-button--main"
            }
        ],
        "all_links": [
            {"text": "Forgot your password?", "href": "/auth/requestPasswordResetCode"}
        ],
        "visible_text": "OrangeHRM Login Username Password Forgot your password?",
        "fetch_source": "simulated_vista_browser",
        "confidence": 1.0
    },
    "DASHBOARD": {
        "current_url": "https://opensource-demo.orangehrmlive.com/web/index.php/dashboard/index",
        "page_title": "OrangeHRM - Dashboard",
        "https": True,
        "headings": ["Dashboard", "Quick Launch", "Time at Work"],
        "input_fields": [],
        "buttons": [
            {"text": "Assign Leave", "class": "oxd-button"},
            {"text": "Leave List", "class": "oxd-button"},
            {"text": "Timesheets", "class": "oxd-button"},
            {"text": "Apply Leave", "class": "oxd-button"}
        ],
        "nav_links": [
            {"text": "Admin", "href": "/web/index.php/admin/viewSystemUsers"},
            {"text": "PIM", "href": "/web/index.php/pim/viewEmployeeList"},
            {"text": "Leave", "href": "/web/index.php/leave/viewLeaveList"},
            {"text": "Time", "href": "/web/index.php/time/viewEmployeeTimesheet"},
            {"text": "Recruitment", "href": "/web/index.php/recruitment/viewCandidates"},
            {"text": "My Info", "href": "/web/index.php/pim/viewMyDetails"},
            {"text": "Performance", "href": "/web/index.php/performance/searchEvaluatePerformanceReview"},
            {"text": "Dashboard", "href": "/web/index.php/dashboard/index"},
            {"text": "Directory", "href": "/web/index.php/directory/viewDirectory"},
            {"text": "Maintenance", "href": "/web/index.php/maintenance/purgeEmployee"},
            {"text": "Buzz", "href": "/web/index.php/buzz/viewBuzz"}
        ],
        "visible_text": "Dashboard Quick Launch Time at Work Assign Leave Leave List Timesheets Apply Leave",
        "fetch_source": "simulated_vista_browser",
        "confidence": 1.0
    },
    "ADMIN": {
        "current_url": "https://opensource-demo.orangehrmlive.com/web/index.php/admin/viewSystemUsers",
        "page_title": "OrangeHRM - Admin",
        "https": True,
        "headings": ["System Users", "User Management"],
        "input_fields": [
            {"type": "text", "name": "username", "placeholder": "Username", "aria_label": "Username"},
            {"type": "text", "name": "employeeName", "placeholder": "Employee Name", "aria_label": "Employee Name"}
        ],
        "buttons": [
            {"text": "Search", "class": "oxd-button oxd-button--medium oxd-button--secondary"},
            {"text": "Reset", "class": "oxd-button oxd-button--medium oxd-button--ghost"},
            {"text": "Add", "class": "oxd-button oxd-button--medium oxd-button--secondary"}
        ],
        "nav_links": [
            {"text": "User Management", "href": "/web/index.php/admin/viewSystemUsers"},
            {"text": "Job", "href": "/web/index.php/admin/viewJobTitleList"},
            {"text": "Organization", "href": "/web/index.php/admin/viewOrganizationGeneralInformation"},
            {"text": "Qualifications", "href": "/web/index.php/admin/qualification"},
            {"text": "Nationalities", "href": "/web/index.php/admin/nationality"},
            {"text": "Corporate Branding", "href": "/web/index.php/admin/displayTheme"},
            {"text": "Configuration", "href": "/web/index.php/admin/listMailConfiguration"}
        ],
        "visible_text": "System Users User Management Search Filter Users Username Employee Name User Role Status Add User",
        "fetch_source": "simulated_vista_browser",
        "confidence": 1.0
    },
    "PIM": {
        "current_url": "https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList",
        "page_title": "OrangeHRM - PIM",
        "https": True,
        "headings": ["Employee Information", "Configuration"],
        "input_fields": [
            {"type": "text", "name": "employeeName", "placeholder": "Employee Name", "aria_label": "Employee Name"},
            {"type": "text", "name": "employeeId", "placeholder": "Employee Id", "aria_label": "Employee Id"}
        ],
        "buttons": [
            {"text": "Search", "class": "oxd-button oxd-button--medium oxd-button--secondary"},
            {"text": "Reset", "class": "oxd-button oxd-button--medium oxd-button--ghost"},
            {"text": "Add", "class": "oxd-button oxd-button--medium oxd-button--secondary"}
        ],
        "nav_links": [
            {"text": "Configuration", "href": "/web/index.php/pim/viewOptionalFields"},
            {"text": "Employee List", "href": "/web/index.php/pim/viewEmployeeList"},
            {"text": "Add Employee", "href": "/web/index.php/pim/addEmployee"},
            {"text": "Reports", "href": "/web/index.php/pim/viewDefinedPredefinedReports"}
        ],
        "visible_text": "Employee Information Configuration Search Employees Employee Name Employee Id Employment Status Include Supervisor Name Job Title Sub Unit Add Employee",
        "fetch_source": "simulated_vista_browser",
        "confidence": 1.0
    },
    "LEAVE": {
        "current_url": "https://opensource-demo.orangehrmlive.com/web/index.php/leave/viewLeaveList",
        "page_title": "OrangeHRM - Leave",
        "https": True,
        "headings": ["Leave List", "Leave Period"],
        "input_fields": [
            {"type": "date", "name": "fromDate", "placeholder": "From Date", "aria_label": "From Date"},
            {"type": "date", "name": "toDate", "placeholder": "To Date", "aria_label": "To Date"}
        ],
        "buttons": [
            {"text": "Search", "class": "oxd-button oxd-button--medium oxd-button--secondary"},
            {"text": "Reset", "class": "oxd-button oxd-button--medium oxd-button--ghost"},
            {"text": "Apply", "class": "oxd-button oxd-button--medium oxd-button--secondary"},
            {"text": "Assign", "class": "oxd-button oxd-button--medium oxd-button--secondary"}
        ],
        "nav_links": [
            {"text": "Apply", "href": "/web/index.php/leave/applyLeave"},
            {"text": "My Leave", "href": "/web/index.php/leave/viewMyLeaveList"},
            {"text": "Entitlements", "href": "/web/index.php/leave/viewLeaveEntitlements"},
            {"text": "Reports", "href": "/web/index.php/leave/viewLeaveReports"},
            {"text": "Configure", "href": "/web/index.php/leave/viewLeaveTypeList"},
            {"text": "Leave List", "href": "/web/index.php/leave/viewLeaveList"},
            {"text": "Assign Leave", "href": "/web/index.php/leave/assignLeave"}
        ],
        "visible_text": "Leave List Leave Period From Date To Date Show Leave with Status Apply Leave Assign Leave My Leave",
        "fetch_source": "simulated_vista_browser",
        "confidence": 1.0
    }
}

# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class VistaBrowserToolSchema(BaseModel):
    """Input schema for VistaBrowserTool."""
    
    action: str = Field(
        ...,
        description=(
            "Browser action to perform. Supported: "
            "Navigate, Type, Click, Wait, Scroll, Hover, Expand, Refresh"
        )
    )
    url: Optional[str] = Field(
        default=None,
        description="Target URL for Navigate action"
    )
    selector: Optional[str] = Field(
        default=None,
        description="CSS selector or element identifier for Type/Click/Hover actions"
    )
    text: Optional[str] = Field(
        default=None,
        description="Text to type into input field (for Type action)"
    )
    duration: Optional[int] = Field(
        default=1000,
        description="Wait duration in milliseconds (for Wait action)"
    )
    direction: Optional[str] = Field(
        default="down",
        description="Scroll direction: 'up' or 'down' (for Scroll action)"
    )

# ============================================================================
# VISTA BROWSER TOOL
# ============================================================================

class VistaBrowserTool(BaseTool):
    """
    Vista Browser Exploration Tool - Simulated browser for AAVA Console training.
    
    **Architecture:**
    - Synchronous operation (no async/Playwright dependencies)
    - Pre-defined PAGES dictionary simulates real application responses
    - Module-level state tracking (_STATE) for session management
    - Uses urllib for HTTP (SSL context, cookies, opener)
    
    **State Management:**
    - _STATE["current_url"]: Current page URL
    - _STATE["fields"]: Dictionary of typed form field values
    - _STATE["loggedin"]: Boolean login status flag
    - _STATE["session_start"]: Session start timestamp
    - _STATE["action_count"]: Total actions performed
    
    **Supported Actions:**
    1. Navigate: Load page (returns LOGIN if not logged in, target page if logged in)
    2. Type: Store text in form field (_STATE["fields"][field_name] = text)
    3. Click: Execute button action (login logic: checks username/password in _STATE["fields"])
    4. Wait: Simulate wait/delay (returns confirmation)
    5. Scroll: Simulate page scroll (returns confirmation)
    6. Hover: Simulate hover action (returns element info)
    7. Expand: Simulate dropdown/accordion expansion (returns confirmation)
    8. Refresh: Reload current page (returns current page data)
    
    **Login Flow:**
    1. Navigate to login URL → returns LOGIN page
    2. Type username → stores in _STATE["fields"]["username"]
    3. Type password → stores in _STATE["fields"]["password"]
    4. Click submit button → validates credentials, sets _STATE["loggedin"] = True
    5. Navigate to any URL → returns appropriate page based on login status
    
    **Output:**
    Returns JSON string for CrewAI agent consumption with structured data.
    """
    
    name: str = "Vista Browser Tool"
    description: str = """
    Simulated browser tool for AAVA Console exploration and testing.
    Supports Navigate, Type, Click, Wait, Scroll, Hover, Expand, Refresh actions.
    Maintains session state for login flows and form interactions.
    Returns structured JSON responses with page data.
    """
    args_schema: Type[BaseModel] = VistaBrowserToolSchema
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize session
        if _STATE["session_start"] is None:
            _STATE["session_start"] = datetime.utcnow().isoformat() + "Z"
    
    def _log(self, msg: str) -> None:
        """Log message with tool name prefix."""
        logging.info(f"[{self.name}] {msg}")
    
    def _run(
        self,
        action: str,
        url: Optional[str] = None,
        selector: Optional[str] = None,
        text: Optional[str] = None,
        duration: int = 1000,
        direction: str = "down",
        **kwargs
    ) -> str:
        """
        Main execution method - synchronous browser simulation.
        
        Args:
            action: Browser action (Navigate, Type, Click, Wait, Scroll, Hover, Expand, Refresh)
            url: Target URL (for Navigate action)
            selector: CSS selector or element identifier (for Type/Click/Hover actions)
            text: Text to type (for Type action)
            duration: Wait duration in milliseconds (for Wait action)
            direction: Scroll direction 'up' or 'down' (for Scroll action)
        
        Returns:
            JSON string with action result for CrewAI agent consumption
        """
        try:
            _STATE["action_count"] += 1
            action_lower = action.lower()
            
            self._log(f"Action #{_STATE['action_count']}: {action} (loggedin={_STATE['loggedin']})")
            
            # Route to appropriate action handler
            if action_lower == "navigate":
                return self._handle_navigate(url)
            elif action_lower == "type":
                return self._handle_type(selector, text)
            elif action_lower == "click":
                return self._handle_click(selector)
            elif action_lower == "wait":
                return self._handle_wait(duration)
            elif action_lower == "scroll":
                return self._handle_scroll(direction)
            elif action_lower == "hover":
                return self._handle_hover(selector)
            elif action_lower == "expand":
                return self._handle_expand(selector)
            elif action_lower == "refresh":
                return self._handle_refresh()
            else:
                return json.dumps({
                    "error": True,
                    "code": "INVALID_ACTION",
                    "message": f"Unknown action: {action}. Supported: Navigate, Type, Click, Wait, Scroll, Hover, Expand, Refresh",
                    "tool": self.name,
                    "action": action
                }, indent=2)
        
        except Exception as exc:
            self._log(f"Error during action '{action}': {exc}")
            return json.dumps({
                "error": True,
                "code": "ACTION_EXECUTION_ERROR",
                "message": str(exc),
                "tool": self.name,
                "action": action
            }, indent=2)
    
    def _handle_navigate(self, url: Optional[str]) -> str:
        """
        Handle Navigate action - load page based on URL and login status.
        
        Logic:
        1. If URL is login page → return LOGIN page
        2. If not logged in and URL is not login → return LOGIN page with redirect notice
        3. If logged in → return appropriate page based on URL path
        """
        if not url:
            return json.dumps({
                "error": True,
                "code": "MISSING_URL",
                "message": "Navigate action requires 'url' parameter",
                "tool": self.name,
                "action": "Navigate"
            }, indent=2)
        
        # Update current URL in state
        _STATE["current_url"] = url
        
        # Parse URL to determine target page
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        self._log(f"Navigate to: {url}")
        
        # Check if login page
        is_login_page = "/auth/login" in path or "/login" in path
        
        # If not logged in and not login page, redirect to login
        if not _STATE["loggedin"] and not is_login_page:
            result = {
                "action": "Navigate",
                "status": "redirect_to_login",
                "message": "User not authenticated. Redirecting to login page.",
                "requested_url": url,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                **PAGES["LOGIN"]
            }
            _STATE["current_url"] = PAGES["LOGIN"]["current_url"]
            return json.dumps(result, indent=2)
        
        # If login page requested
        if is_login_page:
            result = {
                "action": "Navigate",
                "status": "success",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                **PAGES["LOGIN"]
            }
            return json.dumps(result, indent=2)
        
        # If logged in, return appropriate page
        if "/dashboard" in path:
            page_data = PAGES["DASHBOARD"]
        elif "/admin" in path:
            page_data = PAGES["ADMIN"]
        elif "/pim" in path:
            page_data = PAGES["PIM"]
        elif "/leave" in path:
            page_data = PAGES["LEAVE"]
        else:
            # Default to dashboard if logged in
            page_data = PAGES["DASHBOARD"]
        
        result = {
            "action": "Navigate",
            "status": "success",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            **page_data
        }
        
        return json.dumps(result, indent=2)
    
    def _handle_type(self, selector: Optional[str], text: Optional[str]) -> str:
        """
        Handle Type action - store text in form field.
        
        Stores typed values in _STATE["fields"] dictionary for later validation.
        """
        if not selector:
            return json.dumps({
                "error": True,
                "code": "MISSING_SELECTOR",
                "message": "Type action requires 'selector' parameter",
                "tool": self.name,
                "action": "Type"
            }, indent=2)
        
        if not text:
            return json.dumps({
                "error": True,
                "code": "MISSING_TEXT",
                "message": "Type action requires 'text' parameter",
                "tool": self.name,
                "action": "Type"
            }, indent=2)
        
        # Extract field name from selector
        # Supports: input[name='username'], #txtUsername, [name="password"]
        selector_lower = selector.lower()
        
        if "username" in selector_lower:
            field_name = "username"
        elif "password" in selector_lower:
            field_name = "password"
        elif "employee" in selector_lower:
            field_name = "employee_name"
        elif "email" in selector_lower:
            field_name = "email"
        else:
            # Generic field name extraction
            field_name = selector.replace("input[name='", "").replace("']", "").replace("[name=", "").replace("]", "").replace('"', "").replace("#", "")
        
        # Store in state
        _STATE["fields"][field_name] = text
        
        self._log(f"Type '{text}' into {selector} (stored as '{field_name}')")
        
        result = {
            "action": "Type",
            "status": "success",
            "selector": selector,
            "field_name": field_name,
            "text_length": len(text),
            "message": f"Successfully typed {len(text)} characters into {selector}",
            "current_fields": list(_STATE["fields"].keys()),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return json.dumps(result, indent=2)
    
    def _handle_click(self, selector: Optional[str]) -> str:
        """
        Handle Click action - execute button action (e.g., login).
        
        Login Logic:
        - If selector contains 'submit' or 'login' and credentials are in _STATE["fields"]
        - Validates username='Admin' and password='admin123'
        - Sets _STATE["loggedin"] = True on success
        """
        if not selector:
            return json.dumps({
                "error": True,
                "code": "MISSING_SELECTOR",
                "message": "Click action requires 'selector' parameter",
                "tool": self.name,
                "action": "Click"
            }, indent=2)
        
        selector_lower = selector.lower()
        
        # Check if this is a login button click
        is_login_button = any(keyword in selector_lower for keyword in ["submit", "login", "btnlogin"])
        
        if is_login_button:
            # Validate credentials from state
            username = _STATE["fields"].get("username", "")
            password = _STATE["fields"].get("password", "")
            
            self._log(f"Login attempt - username: {username}, password: {'***' if password else '(empty)'}")
            
            # Validate credentials (hardcoded for simulation)
            if username == "Admin" and password == "admin123":
                _STATE["loggedin"] = True
                _STATE["current_url"] = PAGES["DASHBOARD"]["current_url"]
                
                result = {
                    "action": "Click",
                    "status": "success",
                    "selector": selector,
                    "element_type": "submit_button",
                    "login_status": "authenticated",
                    "message": "Login successful. Session established.",
                    "redirect_url": PAGES["DASHBOARD"]["current_url"],
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    **PAGES["DASHBOARD"]
                }
                
                self._log("Login successful")
                return json.dumps(result, indent=2)
            else:
                result = {
                    "action": "Click",
                    "status": "error",
                    "selector": selector,
                    "element_type": "submit_button",
                    "login_status": "failed",
                    "message": "Invalid credentials. Expected username='Admin', password='admin123'",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
                
                self._log("Login failed - invalid credentials")
                return json.dumps(result, indent=2)
        
        # Generic button click
        result = {
            "action": "Click",
            "status": "success",
            "selector": selector,
            "element_type": "button",
            "message": f"Successfully clicked element: {selector}",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return json.dumps(result, indent=2)
    
    def _handle_wait(self, duration: int) -> str:
        """Handle Wait action - simulate delay."""
        # Simulate wait (actual sleep would block agent, so we just acknowledge)
        wait_seconds = duration / 1000.0
        
        self._log(f"Wait {wait_seconds}s")
        
        # Optional: Actually sleep (uncomment if needed for rate limiting)
        # time.sleep(wait_seconds)
        
        result = {
            "action": "Wait",
            "status": "success",
            "duration_ms": duration,
            "duration_seconds": wait_seconds,
            "message": f"Successfully waited {wait_seconds} seconds",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return json.dumps(result, indent=2)
    
    def _handle_scroll(self, direction: str) -> str:
        """Handle Scroll action - simulate page scroll."""
        direction_lower = direction.lower()
        
        if direction_lower not in ["up", "down"]:
            return json.dumps({
                "error": True,
                "code": "INVALID_DIRECTION",
                "message": f"Invalid scroll direction: {direction}. Use 'up' or 'down'",
                "tool": self.name,
                "action": "Scroll"
            }, indent=2)
        
        self._log(f"Scroll {direction_lower}")
        
        result = {
            "action": "Scroll",
            "status": "success",
            "direction": direction_lower,
            "scroll_amount": 500,
            "message": f"Successfully scrolled {direction_lower} by 500 pixels",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return json.dumps(result, indent=2)
    
    def _handle_hover(self, selector: Optional[str]) -> str:
        """Handle Hover action - simulate mouse hover."""
        if not selector:
            return json.dumps({
                "error": True,
                "code": "MISSING_SELECTOR",
                "message": "Hover action requires 'selector' parameter",
                "tool": self.name,
                "action": "Hover"
            }, indent=2)
        
        self._log(f"Hover over {selector}")
        
        # Simulate discovering element info on hover
        element_info = {
            "selector": selector,
            "tooltip": "Element tooltip text",
            "aria_label": "Element description"
        }
        
        result = {
            "action": "Hover",
            "status": "success",
            "selector": selector,
            "element_info": element_info,
            "message": f"Successfully hovered over element: {selector}",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return json.dumps(result, indent=2)
    
    def _handle_expand(self, selector: Optional[str]) -> str:
        """Handle Expand action - simulate dropdown/accordion expansion."""
        if not selector:
            return json.dumps({
                "error": True,
                "code": "MISSING_SELECTOR",
                "message": "Expand action requires 'selector' parameter",
                "tool": self.name,
                "action": "Expand"
            }, indent=2)
        
        self._log(f"Expand {selector}")
        
        # Simulate expanded content
        expanded_content = [
            "Option 1",
            "Option 2",
            "Option 3"
        ]
        
        result = {
            "action": "Expand",
            "status": "success",
            "selector": selector,
            "expanded": True,
            "revealed_options": expanded_content,
            "message": f"Successfully expanded element: {selector}",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return json.dumps(result, indent=2)
    
    def _handle_refresh(self) -> str:
        """Handle Refresh action - reload current page."""
        current_url = _STATE.get("current_url")
        
        if not current_url:
            return json.dumps({
                "error": True,
                "code": "NO_CURRENT_PAGE",
                "message": "No current page to refresh. Navigate to a page first.",
                "tool": self.name,
                "action": "Refresh"
            }, indent=2)
        
        self._log(f"Refresh current page: {current_url}")
        
        # Re-navigate to current URL
        return self._handle_navigate(current_url)
    
    def reset_session(self) -> None:
        """
        Reset session state (useful for testing).
        Clears login status, form fields, and current URL.
        """
        _STATE["current_url"] = None
        _STATE["fields"] = {}
        _STATE["loggedin"] = False
        _STATE["session_start"] = datetime.utcnow().isoformat() + "Z"
        _STATE["action_count"] = 0
        self._log("Session reset")
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get current session state (useful for debugging).
        
        Returns:
            Copy of _STATE dictionary
        """
        return _STATE.copy()


# ============================================================================
# COMPANION TOOLS (Authentication Discovery, Technology Detection)
# ============================================================================

class AuthenticationDiscoveryToolSchema(BaseModel):
    """Input schema for AuthenticationDiscoveryTool."""
    
    page_data: str = Field(
        ...,
        description="JSON string containing page data from VistaBrowserTool Navigate action"
    )


class AuthenticationDiscoveryTool(BaseTool):
    """
    Authentication Discovery Tool - Analyzes page data to identify auth patterns.
    
    Detects:
    - Login forms (username/password fields)
    - OAuth buttons (Sign in with Google, etc.)
    - Multi-factor authentication elements
    - Password reset links
    - Registration links
    """
    
    name: str = "Authentication Discovery Tool"
    description: str = """
    Analyzes page data to discover authentication mechanisms.
    Identifies login forms, OAuth providers, MFA elements, and auth-related links.
    Returns structured JSON with authentication analysis.
    """
    args_schema: Type[BaseModel] = AuthenticationDiscoveryToolSchema
    
    def _run(self, page_data: str, **kwargs) -> str:
        """
        Analyze page data for authentication patterns.
        
        Args:
            page_data: JSON string from VistaBrowserTool Navigate action
        
        Returns:
            JSON string with authentication analysis
        """
        try:
            data = json.loads(page_data)
            
            # Extract authentication indicators
            input_fields = data.get("input_fields", [])
            buttons = data.get("buttons", [])
            all_links = data.get("all_links", [])
            visible_text = data.get("visible_text", "")
            
            # Detect username field
            username_fields = [
                field for field in input_fields
                if any(keyword in field.get("name", "").lower() or keyword in field.get("placeholder", "").lower()
                       for keyword in ["username", "email", "user"])
            ]
            
            # Detect password field
            password_fields = [
                field for field in input_fields
                if field.get("type") == "password" or "password" in field.get("name", "").lower()
            ]
            
            # Detect submit button
            submit_buttons = [
                btn for btn in buttons
                if btn.get("type") == "submit" or any(keyword in btn.get("text", "").lower()
                                                       for keyword in ["login", "sign in", "submit"])
            ]
            
            # Detect password reset link
            password_reset_links = [
                link for link in all_links
                if any(keyword in link.get("text", "").lower()
                       for keyword in ["forgot", "reset", "password"])
            ]
            
            # Determine authentication type
            has_login_form = len(username_fields) > 0 and len(password_fields) > 0 and len(submit_buttons) > 0
            
            auth_type = "none"
            if has_login_form:
                auth_type = "form_based"
            
            # Detect OAuth (common in visible text)
            oauth_providers = []
            for provider in ["Google", "Facebook", "Microsoft", "GitHub", "LinkedIn"]:
                if provider.lower() in visible_text.lower():
                    oauth_providers.append(provider)
            
            if oauth_providers:
                auth_type = "oauth" if auth_type == "none" else "hybrid"
            
            result = {
                "authentication_discovered": has_login_form or len(oauth_providers) > 0,
                "authentication_type": auth_type,
                "login_form": {
                    "detected": has_login_form,
                    "username_fields": username_fields,
                    "password_fields": password_fields,
                    "submit_buttons": submit_buttons
                },
                "oauth_providers": oauth_providers,
                "password_reset_available": len(password_reset_links) > 0,
                "password_reset_links": password_reset_links,
                "recommendations": self._generate_auth_recommendations(
                    has_login_form, oauth_providers, password_reset_links
                ),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            return json.dumps(result, indent=2)
        
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": True,
                "code": "INVALID_JSON",
                "message": f"Failed to parse page_data JSON: {e}",
                "tool": self.name
            }, indent=2)
        except Exception as exc:
            return json.dumps({
                "error": True,
                "code": "ANALYSIS_ERROR",
                "message": str(exc),
                "tool": self.name
            }, indent=2)
    
    def _generate_auth_recommendations(
        self,
        has_login_form: bool,
        oauth_providers: list,
        password_reset_links: list
    ) -> list:
        """Generate authentication testing recommendations."""
        recommendations = []
        
        if has_login_form:
            recommendations.append("Test form-based authentication with valid credentials")
            recommendations.append("Test invalid credentials handling and error messages")
            recommendations.append("Check for CSRF token protection in login form")
        
        if oauth_providers:
            recommendations.append(f"Test OAuth flows for: {', '.join(oauth_providers)}")
        
        if password_reset_links:
            recommendations.append("Test password reset/recovery workflow")
        
        if not has_login_form and not oauth_providers:
            recommendations.append("No authentication mechanism detected - verify page navigation")
        
        return recommendations


class TechnologyDetectionToolSchema(BaseModel):
    """Input schema for TechnologyDetectionTool."""
    
    page_data: str = Field(
        ...,
        description="JSON string containing page data from VistaBrowserTool Navigate action"
    )


class TechnologyDetectionTool(BaseTool):
    """
    Technology Detection Tool - Identifies frontend frameworks and technologies.
    
    Detects:
    - Frontend frameworks (Vue, React, Angular)
    - UI libraries (Bootstrap, Material-UI)
    - API patterns (REST, GraphQL)
    - Build tools (Webpack, Vite)
    """
    
    name: str = "Technology Detection Tool"
    description: str = """
    Analyzes page data to detect frontend technologies and frameworks.
    Identifies Vue, React, Angular, UI libraries, and API patterns.
    Returns structured JSON with technology stack analysis.
    """
    args_schema: Type[BaseModel] = TechnologyDetectionToolSchema
    
    def _run(self, page_data: str, **kwargs) -> str:
        """
        Detect technologies from page data.
        
        Args:
            page_data: JSON string from VistaBrowserTool Navigate action
        
        Returns:
            JSON string with technology detection results
        """
        try:
            data = json.loads(page_data)
            
            visible_text = data.get("visible_text", "")
            current_url = data.get("current_url", "")
            buttons = data.get("buttons", [])
            
            # Framework detection heuristics
            frameworks = []
            ui_libraries = []
            
            # Detect Vue.js (common class patterns)
            button_classes = " ".join(btn.get("class", "") for btn in buttons)
            
            if "oxd-button" in button_classes:
                frameworks.append("Custom Component Library")
                ui_libraries.append("OrangeHRM Design System (oxd-)")
            
            # Detect common UI frameworks
            if "bootstrap" in button_classes.lower():
                ui_libraries.append("Bootstrap")
            if "material" in button_classes.lower() or "mui-" in button_classes.lower():
                ui_libraries.append("Material-UI")
            if "ant-" in button_classes.lower():
                ui_libraries.append("Ant Design")
            
            # API detection (based on URL patterns)
            api_type = "unknown"
            if "/api/" in current_url:
                api_type = "REST"
            elif "/graphql" in current_url:
                api_type = "GraphQL"
            else:
                api_type = "REST (assumed)"
            
            # HTTPS detection
            https_enabled = data.get("https", False)
            
            result = {
                "technology_stack": {
                    "frameworks": frameworks if frameworks else ["Not detected"],
                    "ui_libraries": ui_libraries if ui_libraries else ["Not detected"],
                    "api_type": api_type,
                    "https_enabled": https_enabled
                },
                "confidence": {
                    "frameworks": 0.8 if frameworks else 0.3,
                    "ui_libraries": 0.9 if ui_libraries else 0.2,
                    "api_type": 0.6
                },
                "detected_patterns": {
                    "button_classes": button_classes[:200] if button_classes else "None",
                    "url_patterns": current_url
                },
                "recommendations": [
                    "Inspect network traffic for API endpoint discovery",
                    "Check HTML source for framework-specific attributes",
                    "Analyze JavaScript bundles for build tool detection"
                ],
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            return json.dumps(result, indent=2)
        
        except json.JSONDecodeError as e:
            return json.dumps({
                "error": True,
                "code": "INVALID_JSON",
                "message": f"Failed to parse page_data JSON: {e}",
                "tool": self.name
            }, indent=2)
        except Exception as exc:
            return json.dumps({
                "error": True,
                "code": "DETECTION_ERROR",
                "message": str(exc),
                "tool": self.name
            }, indent=2)


# ============================================================================
# USAGE EXAMPLE (for testing)
# ============================================================================

if __name__ == "__main__":
    # Initialize tool
    browser_tool = VistaBrowserTool()
    auth_tool = AuthenticationDiscoveryTool()
    tech_tool = TechnologyDetectionTool()
    
    print("=" * 80)
    print("VISTA BROWSER TOOL - SIMULATION TEST")
    print("=" * 80)
    
    # 1. Navigate to login page
    print("\n[1] Navigate to login page:")
    result1 = browser_tool._run(
        action="Navigate",
        url="https://opensource-demo.orangehrmlive.com/web/index.php/auth/login"
    )
    print(result1)
    
    # 2. Analyze authentication
    print("\n[2] Analyze authentication mechanisms:")
    auth_result = auth_tool._run(page_data=result1)
    print(auth_result)
    
    # 3. Detect technologies
    print("\n[3] Detect frontend technologies:")
    tech_result = tech_tool._run(page_data=result1)
    print(tech_result)
    
    # 4. Type username
    print("\n[4] Type username:")
    result2 = browser_tool._run(
        action="Type",
        selector="input[name='username']",
        text="Admin"
    )
    print(result2)
    
    # 5. Type password
    print("\n[5] Type password:")
    result3 = browser_tool._run(
        action="Type",
        selector="input[name='password']",
        text="admin123"
    )
    print(result3)
    
    # 6. Click login button
    print("\n[6] Click login button:")
    result4 = browser_tool._run(
        action="Click",
        selector="button[type='submit']"
    )
    print(result4)
    
    # 7. Navigate to PIM module
    print("\n[7] Navigate to PIM module (after login):")
    result5 = browser_tool._run(
        action="Navigate",
        url="https://opensource-demo.orangehrmlive.com/web/index.php/pim/viewEmployeeList"
    )
    print(result5)
    
    # 8. Test wait action
    print("\n[8] Wait 2 seconds:")
    result6 = browser_tool._run(
        action="Wait",
        duration=2000
    )
    print(result6)
    
    # 9. Test scroll action
    print("\n[9] Scroll down:")
    result7 = browser_tool._run(
        action="Scroll",
        direction="down"
    )
    print(result7)
    
    # 10. Get final state
    print("\n[10] Final session state:")
    print(json.dumps(browser_tool.get_state(), indent=2))
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)