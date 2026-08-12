# BrowserAutomationTool - Playwright-Based Dynamic Web Exploration

## Overview

`BrowserAutomationTool` is a CrewAI BaseTool that uses Playwright to handle React.js SPAs and dynamic content requiring JavaScript execution. It complements the existing `BrowserExplorer` (static HTML parsing) with full browser automation capabilities.

## Installation

```bash
# Install Playwright
pip install playwright

# Install Chromium browser
playwright install chromium

# Optional: For nested event loop support (if using in Jupyter/async environments)
pip install nest-asyncio
```

## Key Features

### 1. Browser Automation
- ✅ Headless/headed Chrome browser via Playwright
- ✅ JavaScript execution and React hydration wait strategies
- ✅ Network idle detection for SPA loading completion
- ✅ Custom selector waiting (e.g., `#root`, `.app-loaded`)

### 2. React/SPA Support
- ✅ Auto-detection of React, Vue, Angular frameworks via runtime inspection
- ✅ Wait for framework root elements (`#root`, `#app`, etc.)
- ✅ Extract fully-rendered DOM after client-side hydration
- ✅ Detect SPA vs SSR vs MPA architecture

### 3. Authentication
- ✅ Handle login flows with username/password
- ✅ Session management and cookie persistence
- ✅ Post-login page exploration
- ✅ Auto-detect authentication state (login forms, logout buttons)

### 4. Network Traffic Analysis
- ✅ Capture all network requests during page load
- ✅ Filter and extract API calls (JSON, GraphQL, REST)
- ✅ Resource summary (scripts, stylesheets, XHR, etc.)
- ✅ Endpoint discovery for backend API mapping

### 5. Debugging & Analysis
- ✅ Full-page screenshots saved to `screenshots/` directory
- ✅ Structured JSON output compatible with CrewAI agents
- ✅ Detailed recommendations based on detected architecture
- ✅ Error handling with actionable error messages

## Usage

### Basic Usage

```python
from browser_automation_tool import BrowserAutomationTool

tool = BrowserAutomationTool()

# Explore a React SPA
result_json = tool._run(
    url="https://example.com",
    wait_for_selector="#root",
    capture_network=True,
    take_screenshot=True
)

import json
result = json.loads(result_json)
print(result["rendering"]["framework"])  # "React"
print(result["dom"]["title"])  # Page title
print(result["network"]["api_calls"])  # API endpoints discovered
```

### With Authentication

```python
result_json = tool._run(
    url="https://app.example.com/dashboard",
    authenticate={
        "login_url": "https://app.example.com/login",
        "username": "test@example.com",
        "password": "password123"
    },
    wait_for_selector=".dashboard-loaded",
    capture_network=True
)
```

### Headed Mode (for Debugging)

```python
result_json = tool._run(
    url="https://example.com",
    headless=False,  # Opens visible browser
    wait_timeout=60000,  # 60 second timeout
    take_screenshot=True
)
```

### CrewAI Agent Integration

```python
from crewai import Agent, Task, Crew
from browser_automation_tool import BrowserAutomationTool

# Create agent with the tool
explorer_agent = Agent(
    role="Web Application Explorer",
    goal="Analyze web application architecture and extract interactive elements",
    backstory="Expert in web scraping and browser automation",
    tools=[BrowserAutomationTool()],
    verbose=True
)

# Create task
explore_task = Task(
    description="""
    Explore the React SPA at https://example.com and:
    1. Identify the framework and rendering architecture
    2. Extract all forms and input fields
    3. Capture API endpoints from network traffic
    4. Take a screenshot for documentation
    """,
    agent=explorer_agent,
    expected_output="JSON report with DOM structure, API calls, and screenshots"
)

# Execute
crew = Crew(agents=[explorer_agent], tasks=[explore_task])
result = crew.kickoff()
```

## Output Structure

```json
{
  "url": "https://example.com",
  "timestamp": "2024-08-12T01:21:00Z",
  "execution_time_ms": 2543.21,
  
  "rendering": {
    "architecture": "SPA",
    "framework": "React",
    "hydration_time_ms": 1823.45,
    "evidence": [
      "React runtime detected via window.React or React fiber",
      "Minimal initial content (45 chars) - likely client-side rendered"
    ]
  },
  
  "dom": {
    "title": "Example App - Dashboard",
    "meta": {
      "description": "Modern React application",
      "viewport": "width=device-width, initial-scale=1"
    },
    "forms": [
      {
        "action": "/api/submit",
        "method": "POST",
        "inputs": [
          {
            "name": "email",
            "type": "email",
            "placeholder": "Enter email",
            "required": true
          }
        ]
      }
    ],
    "interactive_elements": {
      "buttons": [
        {"type": "button", "text": "Submit", "id": "submit-btn"}
      ],
      "links": [
        {"type": "link", "href": "/about", "text": "About Us"}
      ]
    },
    "navigation": {
      "nav_elements": [...],
      "internal_links": [...],
      "external_links": [...]
    }
  },
  
  "network": {
    "total_requests": 34,
    "api_calls": [
      {
        "endpoint": "https://api.example.com/users/me",
        "method": "GET",
        "status": 200,
        "content_type": "application/json"
      }
    ],
    "resource_summary": {
      "document": 1,
      "stylesheet": 3,
      "script": 12,
      "xhr": 5,
      "fetch": 3,
      "image": 10
    }
  },
  
  "authentication": {
    "detected": true,
    "login_form_present": false,
    "logged_in": true,
    "evidence": [
      "Logout button detected - user appears logged in",
      "User menu detected - user appears logged in"
    ]
  },
  
  "screenshot_path": "screenshots/example_com_20240812_012100.png",
  
  "recommendations": [
    "[INFO] SPA architecture detected. Full DOM rendered successfully with browser automation.",
    "[FRAMEWORK] React application detected. Consider analyzing React Router routes and component tree.",
    "[AUTH] User appears to be logged in. Explore authenticated sections of the application.",
    "[API] Captured 8 API calls to 4 unique endpoints. Review network.api_calls for details.",
    "[FORMS] Detected 2 forms on page. Review dom.forms for input fields and actions."
  ]
}
```

## Error Handling

```json
{
  "error": true,
  "code": "PLAYWRIGHT_NOT_INSTALLED",
  "message": "Playwright is not installed. Install with: pip install playwright && playwright install chromium",
  "tool": "Browser Automation Tool",
  "url": "https://example.com"
}
```

Common error codes:
- `PLAYWRIGHT_NOT_INSTALLED` - Playwright not installed
- `BROWSER_AUTOMATION_ERROR` - Generic automation error (navigation timeout, selector not found, etc.)

## Integration with Existing Tools

### Decision Flow: BrowserExplorer vs BrowserAutomationTool

```python
# Recommended approach:
# 1. Start with BrowserExplorer (fast, lightweight)
# 2. If SPA detected, escalate to BrowserAutomationTool

from explore_tool import BrowserExplorer
from browser_automation_tool import BrowserAutomationTool

# Phase 1: Quick static analysis
static_tool = BrowserExplorer()
static_result = json.loads(static_tool._run(url="https://example.com"))

# Phase 2: Check if browser automation needed
if static_result["rendering"]["architecture"] == "SPA":
    print("[ESCALATE] SPA detected - using browser automation")
    dynamic_tool = BrowserAutomationTool()
    result = json.loads(dynamic_tool._run(
        url="https://example.com",
        wait_for_selector="#root",
        capture_network=True
    ))
else:
    print("[SUCCESS] Static analysis sufficient")
    result = static_result
```

### Comparison Matrix

| Feature | BrowserExplorer | BrowserAutomationTool |
|---------|----------------|----------------------|
| Speed | Fast (~1-3s) | Slower (~3-10s) |
| JavaScript Execution | ❌ No | ✅ Yes |
| React SPA Support | ❌ Limited | ✅ Full |
| Network Traffic Capture | ❌ No | ✅ Yes |
| Authentication | ❌ No | ✅ Yes |
| Resource Usage | Low | Higher (browser process) |
| Best For | Static sites, SSR, MPA | SPAs, dynamic content, auth flows |

## Advanced Configuration

### Custom Wait Strategies

```python
# Wait for specific content to appear
result = tool._run(
    url="https://example.com",
    wait_for_selector=".data-loaded[data-ready='true']",
    wait_timeout=45000  # 45 seconds
)
```

### Network Traffic Filtering

The tool automatically captures and categorizes:
- **API Calls**: JSON responses, `/api/` paths, GraphQL endpoints
- **XHR Requests**: GET requests with JSON content type
- **Fetch Requests**: POST/PUT/PATCH/DELETE with JSON

Access via `result["network"]["api_calls"]`

### Screenshot Management

Screenshots are saved to `screenshots/` directory with format:
```
{domain}_{timestamp}.png
example_com_20240812_012100.png
```

Use `take_screenshot=False` to disable.

## Performance Considerations

- **Headless Mode**: Always use `headless=True` in production (30% faster)
- **Timeouts**: Adjust `wait_timeout` based on application load time
- **Screenshot Size**: Full-page screenshots can be large (disable for production crawling)
- **Concurrent Execution**: Playwright supports parallel browser contexts

## Troubleshooting

### Playwright Installation Issues

```bash
# If chromium install fails, try manual download
playwright install --force chromium

# Check installation
playwright --version
```

### Timeout Errors

```python
# Increase timeout for slow applications
result = tool._run(
    url="https://slow-app.com",
    wait_timeout=60000,  # 60 seconds
    wait_for_selector=None  # Skip selector wait
)
```

### Authentication Not Working

- Verify login form selectors match your application
- Try `headless=False` to observe browser behavior
- Check for CAPTCHA or bot detection (may require additional handling)

## Future Enhancements

- [ ] Support for multi-step authentication (2FA, OAuth)
- [ ] React Router route extraction from runtime
- [ ] Vue Router and Angular routing analysis
- [ ] WebSocket traffic capture
- [ ] Performance metrics (LCP, FCP, TTI)
- [ ] Accessibility audit integration
- [ ] Video recording for complex flows

## License

Part of Vista-SalesLoft Playwright planner-agent toolkit.