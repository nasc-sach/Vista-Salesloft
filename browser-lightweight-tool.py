"""
LightweightBrowserTool - A lightweight web scraping tool for AAVA console compatibility.

Uses only requests + BeautifulSoup (no Playwright, Selenium, or browser dependencies).
Compatible with CrewAI BaseTool and BrowserAutomationTool output format.
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Type
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class LightweightBrowserInput(BaseModel):
    """Input schema for LightweightBrowserTool."""
    
    url: str = Field(
        ...,
        description="The URL to fetch and analyze"
    )
    method: str = Field(
        default="GET",
        description="HTTP method: GET or POST"
    )
    data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="POST data as key-value pairs"
    )
    auth_username: Optional[str] = Field(
        default=None,
        description="Basic auth username"
    )
    auth_password: Optional[str] = Field(
        default=None,
        description="Basic auth password"
    )
    cookies: Optional[Dict[str, str]] = Field(
        default=None,
        description="Cookies to include in the request"
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional HTTP headers"
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )


class LightweightBrowserTool(BaseTool):
    """
    Lightweight web scraping tool using requests + BeautifulSoup.
    
    This tool provides basic web page exploration without browser dependencies,
    making it compatible with AAVA console environments where Playwright/Selenium
    cannot run.
    
    Features:
    - HTTP GET/POST requests with authentication
    - Extract title, meta tags, forms, links, and text content
    - Handle SSL, timeout, and connection errors gracefully
    - Session and cookie management
    - JSON output compatible with BrowserAutomationTool format
    """
    
    name: str = "lightweight_browser"
    description: str = (
        "Fetch and analyze web pages using lightweight HTTP requests (no browser required). "
        "Extracts page title, meta tags, forms, links, and text content. "
        "Supports GET/POST methods, authentication, and cookie management. "
        "Use this tool when browser automation is not available or not needed."
    )
    args_schema: Type[BaseModel] = LightweightBrowserInput
    
    USER_AGENT: str = "Vista-Planner/1.0 (Lightweight)"
    REQUEST_TIMEOUT: int = 30
    MAX_CONTENT_PREVIEW: int = 50_000
    
    def __init__(self, **kwargs):
        """Initialize the tool."""
        super().__init__(**kwargs)
        self._session: Optional[requests.Session] = None
    
    def _get_session(self) -> requests.Session:
        """Get or create a requests session with default headers."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": self.USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            })
        return self._session
    
    def _fetch_page(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        auth: Optional[Tuple[str, str]] = None,
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30
    ) -> Tuple[requests.Response, BeautifulSoup]:
        """
        Fetch a web page and parse it with BeautifulSoup.
        
        Args:
            url: The URL to fetch
            method: HTTP method (GET or POST)
            data: POST data
            auth: Tuple of (username, password) for basic auth
            cookies: Dictionary of cookies
            headers: Additional headers
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (response, soup)
            
        Raises:
            requests.RequestException: On HTTP errors
        """
        session = self._get_session()
        
        # Apply custom headers if provided
        request_headers = {}
        if headers:
            request_headers.update(headers)
        
        # Apply cookies if provided
        if cookies:
            session.cookies.update(cookies)
        
        # Make the request
        method = method.upper()
        if method == "POST":
            response = session.post(
                url,
                data=data,
                auth=auth,
                headers=request_headers if request_headers else None,
                timeout=timeout,
                allow_redirects=True,
                verify=True
            )
        else:  # GET
            response = session.get(
                url,
                auth=auth,
                headers=request_headers if request_headers else None,
                timeout=timeout,
                allow_redirects=True,
                verify=True
            )
        
        response.raise_for_status()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        return response, soup
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find("title")
        return title_tag.get_text(strip=True) if title_tag else ""
    
    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract meta tags as a dictionary."""
        meta_dict = {}
        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")
            if name and content:
                meta_dict[name] = content
        return meta_dict
    
    def _extract_forms(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """
        Extract forms with their inputs.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative actions
            
        Returns:
            List of form dictionaries
        """
        forms = []
        for form in soup.find_all("form"):
            form_data = {
                "id": form.get("id"),
                "name": form.get("name"),
                "action": urljoin(base_url, form.get("action", "")),
                "method": form.get("method", "GET").upper(),
                "inputs": []
            }
            
            # Extract form inputs
            for input_tag in form.find_all(["input", "textarea", "select"]):
                input_data = {
                    "type": input_tag.name,
                    "name": input_tag.get("name"),
                    "id": input_tag.get("id"),
                    "value": input_tag.get("value"),
                    "placeholder": input_tag.get("placeholder"),
                    "required": input_tag.has_attr("required")
                }
                
                # For input elements, get the input type
                if input_tag.name == "input":
                    input_data["input_type"] = input_tag.get("type", "text")
                
                # For select elements, get options
                if input_tag.name == "select":
                    options = []
                    for option in input_tag.find_all("option"):
                        options.append({
                            "value": option.get("value"),
                            "text": option.get_text(strip=True)
                        })
                    input_data["options"] = options
                
                form_data["inputs"].append(input_data)
            
            forms.append(form_data)
        
        return forms
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, List[Dict[str, str]]]:
        """
        Extract links and categorize as internal or external.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for determining internal vs external
            
        Returns:
            Dictionary with 'internal' and 'external' link lists
        """
        base_domain = urlparse(base_url).netloc
        internal_links = []
        external_links = []
        seen = set()
        
        for link in soup.find_all("a", href=True):
            href = link.get("href")
            absolute_url = urljoin(base_url, href)
            
            # Skip duplicates, anchors, and javascript
            if (absolute_url in seen or 
                href.startswith("#") or 
                href.startswith("javascript:") or
                href.startswith("mailto:")):
                continue
            
            seen.add(absolute_url)
            
            link_data = {
                "url": absolute_url,
                "text": link.get_text(strip=True)[:100],  # Limit text length
                "title": link.get("title")
            }
            
            # Categorize as internal or external
            link_domain = urlparse(absolute_url).netloc
            if link_domain == base_domain or link_domain == "":
                internal_links.append(link_data)
            else:
                external_links.append(link_data)
        
        return {
            "internal": internal_links[:100],  # Limit to 100 links
            "external": external_links[:50]    # Limit to 50 external links
        }
    
    def _extract_buttons(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract button elements."""
        buttons = []
        for button in soup.find_all(["button", "input"]):
            if button.name == "input" and button.get("type") not in ["submit", "button", "reset"]:
                continue
            
            button_data = {
                "id": button.get("id"),
                "name": button.get("name"),
                "type": button.get("type"),
                "text": button.get_text(strip=True) if button.name == "button" else button.get("value", ""),
                "class": button.get("class")
            }
            buttons.append(button_data)
        
        return buttons[:50]  # Limit to 50 buttons
    
    def _extract_content_summary(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Extract and summarize text content from the page.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary with text preview, character count, and word count
        """
        # Create a copy to avoid modifying the original
        working = BeautifulSoup(str(soup), "html.parser")
        
        # Remove script, style, and other non-content tags
        for tag in working(["script", "style", "noscript", "iframe", "svg"]):
            tag.decompose()
        
        # Extract text
        text = working.get_text(" ", strip=True)
        
        # Calculate statistics
        words = text.split()
        
        return {
            "preview": text[:self.MAX_CONTENT_PREVIEW],
            "characters": len(text),
            "words": len(words),
            "truncated": len(text) > self.MAX_CONTENT_PREVIEW
        }
    
    def _extract_navigation(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Extract navigation element counts."""
        return {
            "nav_elements": len(soup.find_all("nav")),
            "header_elements": len(soup.find_all("header")),
            "footer_elements": len(soup.find_all("footer")),
            "menu_items": len(soup.find_all(["ul", "ol"], class_=lambda c: c and ("menu" in str(c).lower() or "nav" in str(c).lower())))
        }
    
    def _run(
        self,
        url: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        auth_username: Optional[str] = None,
        auth_password: Optional[str] = None,
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: int = 30,
        **kwargs
    ) -> str:
        """
        Execute the lightweight browser tool.
        
        Args:
            url: The URL to fetch
            method: HTTP method (GET or POST)
            data: POST data
            auth_username: Basic auth username
            auth_password: Basic auth password
            cookies: Cookies dictionary
            headers: Additional headers
            timeout: Request timeout in seconds
            
        Returns:
            JSON string with structured page data
        """
        start_time = time.time()
        errors = []
        warnings = []
        success = False
        result = {
            "url": url,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "execution_time_ms": 0,
            "success": False,
            "method": method.upper(),
            "rendering": {
                "architecture": "lightweight-http",
                "framework": "requests + BeautifulSoup",
                "javascript": False,
                "note": "Static HTML analysis only - JavaScript not executed"
            },
            "dom": {},
            "errors": [],
            "warnings": []
        }
        
        try:
            # Prepare authentication
            auth = None
            if auth_username and auth_password:
                auth = (auth_username, auth_password)
            
            # Fetch and parse the page
            response, soup = self._fetch_page(
                url=url,
                method=method,
                data=data,
                auth=auth,
                cookies=cookies,
                headers=headers,
                timeout=timeout
            )
            
            # Extract all page data
            result["dom"] = {
                "title": self._extract_title(soup),
                "meta": self._extract_meta_tags(soup),
                "forms": self._extract_forms(soup, response.url),
                "interactive_elements": {
                    "buttons": self._extract_buttons(soup),
                    "links": self._extract_links(soup, response.url)
                },
                "navigation": self._extract_navigation(soup),
                "content": self._extract_content_summary(soup)
            }
            
            # Add response metadata
            result["response"] = {
                "status_code": response.status_code,
                "content_type": response.headers.get("Content-Type", ""),
                "encoding": response.encoding,
                "final_url": response.url,
                "redirected": response.url != url
            }
            
            # Add warnings for common issues
            if not result["dom"]["title"]:
                warnings.append("Page has no title tag")
            
            if not result["dom"]["meta"]:
                warnings.append("Page has no meta tags")
            
            if response.url != url:
                warnings.append(f"Request was redirected from {url} to {response.url}")
            
            success = True
            
        except requests.exceptions.SSLError as e:
            errors.append({
                "type": "ssl_error",
                "message": f"SSL certificate verification failed: {str(e)}",
                "suggestion": "Try setting verify=False (not recommended for production)"
            })
        
        except requests.exceptions.Timeout as e:
            errors.append({
                "type": "timeout_error",
                "message": f"Request timed out after {timeout} seconds",
                "suggestion": "Increase timeout or check if the server is responding"
            })
        
        except requests.exceptions.ConnectionError as e:
            errors.append({
                "type": "connection_error",
                "message": f"Failed to connect to {url}: {str(e)}",
                "suggestion": "Check URL and network connectivity"
            })
        
        except requests.exceptions.HTTPError as e:
            errors.append({
                "type": "http_error",
                "message": f"HTTP error: {str(e)}",
                "status_code": e.response.status_code if e.response else None,
                "suggestion": "Check URL and authentication credentials"
            })
        
        except requests.exceptions.RequestException as e:
            errors.append({
                "type": "request_error",
                "message": f"Request failed: {str(e)}",
                "suggestion": "Check URL format and network configuration"
            })
        
        except Exception as e:
            errors.append({
                "type": "unexpected_error",
                "message": f"Unexpected error: {str(e)}",
                "suggestion": "Check input parameters and try again"
            })
        
        # Finalize result
        execution_time = (time.time() - start_time) * 1000
        result["execution_time_ms"] = round(execution_time, 2)
        result["success"] = success
        result["errors"] = errors
        result["warnings"] = warnings
        
        return json.dumps(result, indent=2)


# Export for easy import
__all__ = ["LightweightBrowserTool", "LightweightBrowserInput"]


# Example usage
if __name__ == "__main__":
    # Create tool instance
    tool = LightweightBrowserTool()
    
    # Example 1: Simple GET request
    print("Example 1: Fetching example.com")
    print("=" * 80)
    result = tool._run(url="https://example.com")
    print(result)
    print("\n")
    
    # Example 2: With custom headers
    print("Example 2: Fetching with custom headers")
    print("=" * 80)
    result = tool._run(
        url="https://httpbin.org/headers",
        headers={"X-Custom-Header": "test-value"}
    )
    print(result)
    print("\n")
    
    # Example 3: POST request
    print("Example 3: POST request with data")
    print("=" * 80)
    result = tool._run(
        url="https://httpbin.org/post",
        method="POST",
        data={"key1": "value1", "key2": "value2"}
    )
    print(result)