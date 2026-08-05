import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Type
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

from crewai.tools import BaseTool


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

_JS_BUNDLE_MAX_BYTES = 2_000_000   # 2 MB cap for bundle download
_CSS_MAX_BYTES       =   500_000   # 500 KB cap per stylesheet

# Confidence bands
_HIGH   = "high"
_MEDIUM = "medium"
_LOW    = "low"
_NONE   = "none"

# Evidence levels
_OBSERVED = "observed"
_INFERRED = "inferred"
_UNKNOWN  = "unknown"


# --------------------------------------------------------------------------- #
# Schema
# --------------------------------------------------------------------------- #

class BrowserExplorerSchema(BaseModel):
    """Input schema for Browser Explorer."""

    url: str = Field(
        ...,
        description="Target application URL to explore."
    )


# --------------------------------------------------------------------------- #
# Tool
# --------------------------------------------------------------------------- #

class BrowserExplorer(BaseTool):
    """
    Static Application Intelligence Engine

    Downloads the HTML shell of a web application, detects whether it is a
    SPA/SSR/MPA, then optionally fetches referenced JS bundles and CSS files
    to extract routes, API endpoints, page modules, state-management patterns,
    business-domain keywords, and authentication clues — all without executing
    JavaScript.

    Every finding is tagged with an evidence level
    (observed / inferred / unknown) and a per-section confidence score,
    so downstream agents can reason accurately even when the rendered DOM
    is not available.
    """

    name: str = "Vista Browser Explore Tool"

    description: str = (
        "Performs deep static analysis of a web application — HTML shell, "
        "JS bundles, CSS — and returns a rich intelligence report with "
        "evidence-qualified findings and per-section confidence scores."
    )

    args_schema: Type[BaseModel] = BrowserExplorerSchema

    USER_AGENT: str = (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/138 Safari/537.36"
    )

    REQUEST_TIMEOUT: int = 300

    # ------------------------------------------------------------------ #
    # Logging
    # ------------------------------------------------------------------ #

    def _log(self, message: str) -> None:
        logging.getLogger(self.name).info(message)

    # ------------------------------------------------------------------ #
    # HTTP helpers
    # ------------------------------------------------------------------ #

    def _session(self) -> requests.Session:
        s = requests.Session()
        s.headers.update({"User-Agent": self.USER_AGENT})
        return s

    def _fetch_page(self, url: str) -> Tuple[requests.Response, BeautifulSoup]:
        self._log(f"Connecting to {url}")
        session = self._session()
        response = session.get(
            url,
            timeout=self.REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        self._log(f"Fetched HTML shell ({response.status_code}) — "
                  f"{len(response.content):,} bytes")
        return response, soup

    def _fetch_text_asset(
        self,
        url: str,
        max_bytes: int,
        label: str,
    ) -> Optional[str]:
        """Download a text asset (JS or CSS) up to *max_bytes*."""
        try:
            session = self._session()
            resp = session.get(
                url,
                timeout=60,
                stream=True,
            )
            resp.raise_for_status()
            chunks: List[bytes] = []
            total = 0
            for chunk in resp.iter_content(chunk_size=65536):
                total += len(chunk)
                chunks.append(chunk)
                if total >= max_bytes:
                    self._log(f"{label} truncated at {max_bytes:,} bytes")
                    break
            text = b"".join(chunks).decode("utf-8", errors="replace")
            self._log(f"Fetched {label} — {total:,} bytes")
            return text
        except Exception as exc:
            self._log(f"Could not fetch {label}: {exc}")
            return None

    # ------------------------------------------------------------------ #
    # HTTP INFORMATION
    # ------------------------------------------------------------------ #

    def _extract_http_info(self, response: requests.Response) -> dict:
        raw_length = response.headers.get("Content-Length")
        try:
            content_length = int(raw_length) if raw_length else len(response.content)
        except ValueError:
            content_length = len(response.content)

        return {
            "requested_url": response.request.url,
            "final_url": response.url,
            "status_code": response.status_code,
            "reason": response.reason,
            "encoding": response.encoding,
            "content_type": response.headers.get("Content-Type"),
            "content_length_bytes": content_length,
            "server": response.headers.get("Server"),
            "powered_by": response.headers.get("X-Powered-By"),
            "redirected": len(response.history) > 0,
            "redirect_chain": [h.url for h in response.history],
            "headers": dict(response.headers),
        }

    # ------------------------------------------------------------------ #
    # RENDERING ARCHITECTURE DETECTION
    # ------------------------------------------------------------------ #

    def _detect_rendering_architecture(
        self,
        soup: BeautifulSoup,
        response: requests.Response,
        scripts_info: dict,
    ) -> dict:
        """
        Determine whether the page is a SPA shell, SSR, or MPA.

        Indicators:
          SPA shell  — tiny HTML, single root div, JS module bundle, no nav links
          SSR        — large HTML with real content, may have hydration markers
          MPA        — multiple pages of plain HTML, no single root div
        """
        html_bytes = len(response.content)
        raw_text   = soup.get_text(" ", strip=True)
        word_count = len(raw_text.split())

        html_str   = str(soup).lower()

        # Root element fingerprints
        spa_roots = {
            "react":  bool(soup.find(id="root")),
            "react_app": bool(soup.find(id="app")),
            "next":   bool(soup.find(id="__next")),
            "nuxt":   bool(soup.find(id="__nuxt")),
            "ember":  bool(soup.find(id="ember")),
        }
        any_spa_root = any(spa_roots.values())

        # Module / hashed bundle script
        has_module_script = scripts_info.get("modules", 0) > 0
        has_hashed_bundle = any(
            re.search(r"-[a-zA-Z0-9]{6,12}\.(js|mjs)", src)
            for src in (scripts_info.get("external") or [])
        )

        # SSR hydration markers
        hydration_markers = [
            "__NEXT_DATA__", "__NUXT__", "ng-server-context",
            "data-server-rendered", "data-reactroot",
        ]
        has_hydration = any(m.lower() in html_str for m in hydration_markers)

        # Decide
        if any_spa_root and (has_module_script or has_hashed_bundle) and word_count < 200:
            arch = "SPA"
            confidence = _HIGH
            evidence = _OBSERVED
            notes = (
                "HTML shell only — rendered DOM requires JavaScript execution. "
                "Static analysis covers bundle intelligence only."
            )
        elif has_hydration:
            arch = "SSR"
            confidence = _HIGH
            evidence = _OBSERVED
            notes = "Server-side rendered page with hydration markers detected."
        elif html_bytes > 20_000 and word_count > 300:
            arch = "MPA/SSR"
            confidence = _MEDIUM
            evidence = _INFERRED
            notes = "Large HTML content suggests server-rendered multi-page application."
        else:
            arch = "Unknown"
            confidence = _LOW
            evidence = _UNKNOWN
            notes = "Insufficient signals to determine rendering architecture."

        return {
            "architecture": arch,
            "confidence": confidence,
            "evidence": evidence,
            "html_bytes": html_bytes,
            "word_count": word_count,
            "spa_root_detected": any_spa_root,
            "spa_roots_found": {k: v for k, v in spa_roots.items() if v},
            "has_module_script": has_module_script,
            "has_hashed_bundle": has_hashed_bundle,
            "has_hydration_markers": has_hydration,
            "notes": notes,
        }

    # ------------------------------------------------------------------ #
    # PAGE INFORMATION
    # ------------------------------------------------------------------ #

    def _extract_page_information(
        self,
        soup: BeautifulSoup,
        response: requests.Response,
    ) -> dict:
        html_tag  = soup.find("html")
        language  = html_tag.get("lang") if html_tag else None
        title     = soup.title.get_text(strip=True) if soup.title else None

        viewport = description = keywords = author = None
        generator = robots = theme_color = canonical = favicon = None

        for meta in soup.find_all("meta"):
            name = meta.get("name", "").lower()
            if name == "viewport":
                viewport = meta.get("content")
            elif name == "description":
                description = meta.get("content")
            elif name == "keywords":
                keywords = meta.get("content")
            elif name == "author":
                author = meta.get("content")
            elif name == "generator":
                generator = meta.get("content")
            elif name == "robots":
                robots = meta.get("content")
            elif name == "theme-color":
                theme_color = meta.get("content")

        link = soup.find("link", rel="canonical")
        if link:
            canonical = link.get("href")

        for tag in soup.find_all("link"):
            rel_list = tag.get("rel") or []
            if any("icon" in r.lower() for r in rel_list):
                favicon = tag.get("href")
                break

        return {
            "title": title,
            "language": language,
            "encoding": response.encoding,
            "description": description,
            "keywords": keywords,
            "author": author,
            "generator": generator,
            "viewport": viewport,
            "robots": robots,
            "theme_color": theme_color,
            "canonical": canonical,
            "favicon": favicon,
        }

    # ------------------------------------------------------------------ #
    # META TAGS
    # ------------------------------------------------------------------ #

    def _extract_meta_tags(self, soup: BeautifulSoup) -> dict:
        metadata: Dict[str, dict] = {
            "standard": {},
            "open_graph": {},
            "twitter": {},
        }
        for meta in soup.find_all("meta"):
            if meta.get("name"):
                metadata["standard"][meta["name"]] = meta.get("content")
            if meta.get("property"):
                prop = meta["property"]
                if prop.startswith("og:"):
                    metadata["open_graph"][prop] = meta.get("content")
            if meta.get("name", "").startswith("twitter:"):
                metadata["twitter"][meta["name"]] = meta.get("content")
        return metadata

    # ------------------------------------------------------------------ #
    # SCRIPTS (HTML shell)
    # ------------------------------------------------------------------ #

    def _extract_scripts(self, soup: BeautifulSoup) -> dict:
        scripts: Dict[str, object] = {
            "external": [],
            "inline": 0,
            "async": 0,
            "defer": 0,
            "modules": 0,
        }
        for script in soup.find_all("script"):
            src = script.get("src")
            if src:
                scripts["external"].append(src)          # type: ignore[union-attr]
            else:
                scripts["inline"] = int(scripts["inline"]) + 1  # type: ignore[arg-type]
            if script.has_attr("async"):
                scripts["async"] = int(scripts["async"]) + 1    # type: ignore[arg-type]
            if script.has_attr("defer"):
                scripts["defer"] = int(scripts["defer"]) + 1    # type: ignore[arg-type]
            if script.get("type") == "module":
                scripts["modules"] = int(scripts["modules"]) + 1  # type: ignore[arg-type]
        return scripts

    # ------------------------------------------------------------------ #
    # STYLESHEETS (HTML shell)
    # ------------------------------------------------------------------ #

    def _extract_stylesheets(self, soup: BeautifulSoup) -> dict:
        css: Dict[str, object] = {"external": [], "inline_blocks": 0}
        for link in soup.find_all("link", rel="stylesheet"):
            css["external"].append(link.get("href"))          # type: ignore[union-attr]
        css["inline_blocks"] = len(soup.find_all("style"))
        return css

    # ------------------------------------------------------------------ #
    # TECHNOLOGY DETECTION (HTML shell — with confidence)
    # ------------------------------------------------------------------ #

    _FRAMEWORK_FINGERPRINTS: Dict[str, str] = {
        # Asset / root element patterns only — no broad "react" keyword
        "React":      r'id="root"|id=\'root\'|/assets/index\.[a-z0-9]+\.js',
        "Next.js":    r'id="__next"|/_next/static',
        "Angular":    r'ng-version|ng-app|angular\.js',
        "Vue":        r'id="app"|__vue_app__|/_nuxt/',
        "Nuxt":       r'id="__nuxt"|/_nuxt/',
        "Svelte":     r'__svelte|svelte-',
        "Vite":       r'type="module".*?vite|vite\.config',
    }

    _CSS_FINGERPRINTS: Dict[str, str] = {
        "Bootstrap":   r"bootstrap",
        "Tailwind":    r"tailwind",
        "Material UI": r'mui|material-ui',
        "Bulma":       r"bulma",
        "Foundation":  r"foundation\.min|foundation\.css",
    }

    _LIB_FINGERPRINTS: Dict[str, str] = {
        "jQuery":      r"jquery",
        "Chart.js":    r"chart\.js",
        "FontAwesome": r"font-awesome|fontawesome",
        "Lodash":      r"lodash",
        "Axios":       r"/axios",
    }

    _ANALYTICS_FINGERPRINTS: Dict[str, str] = {
        "Google Analytics":    r"gtag\(|google-analytics",
        "Google Tag Manager":  r"googletagmanager\.com",
        "Hotjar":              r"hotjar",
        "Segment":             r"analytics\.js|segment\.com",
        "Mixpanel":            r"mixpanel",
    }

    _CDN_FINGERPRINTS: Dict[str, str] = {
        "Cloudflare": r"cloudflare",
        "Fastly":     r"fastly",
        "Akamai":     r"akamai",
    }

    def _detect_technologies(self, soup: BeautifulSoup) -> dict:
        html = str(soup)   # preserve case for attribute values

        detected: Dict[str, List[str]] = {
            "frontend": [],
            "css_frameworks": [],
            "javascript_libraries": [],
            "analytics": [],
            "cdn": [],
        }

        for tech, pattern in self._FRAMEWORK_FINGERPRINTS.items():
            if re.search(pattern, html, re.IGNORECASE):
                if tech not in detected["frontend"]:
                    detected["frontend"].append(tech)

        for tech, pattern in self._CSS_FINGERPRINTS.items():
            if re.search(pattern, html, re.IGNORECASE):
                if tech not in detected["css_frameworks"]:
                    detected["css_frameworks"].append(tech)

        for tech, pattern in self._LIB_FINGERPRINTS.items():
            if re.search(pattern, html, re.IGNORECASE):
                if tech not in detected["javascript_libraries"]:
                    detected["javascript_libraries"].append(tech)

        for tech, pattern in self._ANALYTICS_FINGERPRINTS.items():
            if re.search(pattern, html, re.IGNORECASE):
                if tech not in detected["analytics"]:
                    detected["analytics"].append(tech)

        for tech, pattern in self._CDN_FINGERPRINTS.items():
            if re.search(pattern, html, re.IGNORECASE):
                if tech not in detected["cdn"]:
                    detected["cdn"].append(tech)

        return detected

    # ------------------------------------------------------------------ #
    # JS BUNDLE INTELLIGENCE
    # ------------------------------------------------------------------ #

    def _pick_primary_bundle(
        self,
        external_scripts: List[str],
        base_url: str,
    ) -> Optional[str]:
        """Pick the largest / most likely app bundle URL."""
        candidates = []
        for src in external_scripts:
            absolute = urljoin(base_url, src)
            # Prefer hashed Vite/webpack bundles
            if re.search(r"-[a-zA-Z0-9]{6,12}\.(js|mjs)$", src):
                candidates.insert(0, absolute)
            elif re.search(r"\.(js|mjs)$", src, re.IGNORECASE):
                candidates.append(absolute)
        return candidates[0] if candidates else None

    def _analyze_js_bundle(
        self,
        bundle_text: str,
        base_url: str,
    ) -> dict:
        """
        Static analysis of a minified JS bundle.
        Extracts route names, API patterns, state-management hints,
        and semantic page/module identifiers.
        """
        intelligence: Dict[str, object] = {
            "size_bytes": len(bundle_text.encode("utf-8")),
            "routes_inferred": [],
            "api_endpoints_inferred": [],
            "graphql_detected": False,
            "state_management": [],
            "page_modules": [],
            "auth_hints": [],
            "crud_hints": [],
            "framework_hints": [],
            "evidence": _INFERRED,
        }

        # ---- Route / page name patterns -------------------------------- #
        route_patterns = [
            r'path\s*:\s*["\']([/a-zA-Z0-9_\-:*?]+)["\']',          # path: "/login"
            r'route\s*:\s*["\']([/a-zA-Z0-9_\-:*?]+)["\']',
            r'to\s*:\s*["\']([/a-zA-Z0-9_\-:*?]+)["\']',             # to: "/cart"
            r'"([/][a-zA-Z0-9_\-]{2,}(?:/[a-zA-Z0-9_\-:]+)*)"',     # "/checkout/step"
            r"'([/][a-zA-Z0-9_\-]{2,}(?:/[a-zA-Z0-9_\-:]+)*)'",
        ]
        routes: set = set()
        for pat in route_patterns:
            for m in re.finditer(pat, bundle_text):
                candidate = m.group(1)
                # Filter out obvious non-routes
                if not re.search(r"\.(css|js|png|jpg|svg|woff|ttf)$", candidate, re.I):
                    routes.add(candidate)

        # Keep only plausible routes (short, path-like)
        intelligence["routes_inferred"] = sorted(
            r for r in routes if len(r) < 80 and r.count("/") <= 5
        )[:50]

        # ---- API endpoint patterns ------------------------------------- #
        api_patterns = [
            r'["\`](/api/[a-zA-Z0-9_/\-{}:]+)["\`]',
            r'["\`](/v[0-9]+/[a-zA-Z0-9_/\-{}:]+)["\`]',
            r'fetch\(["\`]([^"\'`\s]{4,})["\`]',
            r'axios\.[a-z]+\(["\`]([^"\'`\s]{4,})["\`]',
        ]
        endpoints: set = set()
        for pat in api_patterns:
            for m in re.finditer(pat, bundle_text):
                ep = m.group(1)
                if re.search(r"^/", ep) and len(ep) < 120:
                    endpoints.add(ep)
        intelligence["api_endpoints_inferred"] = sorted(endpoints)[:50]

        # ---- GraphQL -------------------------------------------------- #
        intelligence["graphql_detected"] = bool(
            re.search(r"graphql|gql`|useQuery|useMutation", bundle_text, re.IGNORECASE)
        )

        # ---- State management ----------------------------------------- #
        sm_hints = []
        patterns_sm = {
            "Redux":         r"createStore|configureStore|useSelector|useDispatch",
            "Zustand":       r"create\(\s*\(set",
            "Pinia":         r"defineStore",
            "MobX":          r"observable|makeObservable|action\(",
            "TanStack Query":r"useQuery|QueryClient|QueryClientProvider",
            "Vuex":          r"Vuex\.Store|createStore\(",
            "NgRx":          r"@ngrx|createReducer|createAction",
            "Jotai":         r"atom\(",
            "Recoil":        r"RecoilRoot|atom\(",
        }
        for lib, pat in patterns_sm.items():
            if re.search(pat, bundle_text):
                sm_hints.append(lib)
        intelligence["state_management"] = sm_hints

        # ---- Page / module names -------------------------------------- #
        # Capture chunk / lazy-loaded component names
        module_patterns = [
            r'chunk\s*["\']([a-zA-Z][a-zA-Z0-9_\-]+)["\']',
            r'component\s*:\s*\(\s*\)\s*=>\s*import\(["\'].*?/([a-zA-Z][a-zA-Z0-9_\-]+)["\']',
            r'loadComponent\(["\'].*?/([a-zA-Z][a-zA-Z0-9_\-]+)["\']',
            r'webpackChunkName:\s*["\']([a-zA-Z][a-zA-Z0-9_\-]+)["\']',
        ]
        modules: set = set()
        for pat in module_patterns:
            for m in re.finditer(pat, bundle_text, re.IGNORECASE):
                modules.add(m.group(1))
        intelligence["page_modules"] = sorted(modules)[:40]

        # ---- Auth hints ---------------------------------------------- #
        auth_keywords = {
            "login":           r"\blogin\b",
            "logout":          r"\blogout\b",
            "register":        r"\bregister\b",
            "password":        r"\bpassword\b",
            "token":           r"\btoken\b",
            "jwt":             r"\bjwt\b",
            "oauth":           r"\boauth\b",
            "refresh_token":   r"refresh.?token",
            "authorization":   r"Authorization",
            "bearer":          r"Bearer ",
            "session":         r"\bsession\b",
            "okta":            r"\bokta\b",
            "auth0":           r"\bauth0\b",
            "cognito":         r"\bcognito\b",
        }
        found_auth = []
        for hint, pat in auth_keywords.items():
            if re.search(pat, bundle_text, re.IGNORECASE):
                found_auth.append(hint)
        intelligence["auth_hints"] = found_auth

        # ---- CRUD hints ---------------------------------------------- #
        crud_keywords = ["create", "add", "edit", "update", "delete", "remove", "save", "submit"]
        intelligence["crud_hints"] = [
            kw for kw in crud_keywords
            if re.search(rf"\b{kw}\b", bundle_text, re.IGNORECASE)
        ]

        # ---- Framework hints (inside bundle) -------------------------- #
        fw_hints = []
        if re.search(r"React\.createElement|jsx\(|_jsx\(", bundle_text):
            fw_hints.append("React")
        if re.search(r"createApp\(|defineComponent\(", bundle_text):
            fw_hints.append("Vue")
        if re.search(r"@angular/core|platformBrowser", bundle_text):
            fw_hints.append("Angular")
        if re.search(r"SvelteComponent|mount\(document", bundle_text):
            fw_hints.append("Svelte")
        intelligence["framework_hints"] = fw_hints

        return intelligence

    # ------------------------------------------------------------------ #
    # CSS INTELLIGENCE
    # ------------------------------------------------------------------ #

    def _analyze_css(self, css_text: str) -> dict:
        """Extract semantic clues from bundled CSS."""
        intelligence: Dict[str, object] = {
            "size_bytes": len(css_text.encode("utf-8")),
            "class_hints": [],
            "page_hints": [],
            "component_hints": [],
            "evidence": _INFERRED,
        }

        # Page / module names from class selectors
        page_selector_patterns = [
            r'\.([a-z][a-z0-9]*[-_](?:page|view|screen|route|panel|modal|drawer|overlay))',
            r'\.(login|logout|register|signup|dashboard|inventory|cart|checkout|profile|settings)',
            r'\.(header|footer|sidebar|navbar|nav-bar|topbar|breadcrumb)',
        ]
        page_hits: set = set()
        for pat in page_selector_patterns:
            for m in re.finditer(pat, css_text, re.IGNORECASE):
                page_hits.add(m.group(1).lower())
        intelligence["page_hints"] = sorted(page_hits)[:40]

        # Component / widget names
        component_patterns = [
            r'\.(btn|button|input|form|card|table|badge|chip|tag|avatar|icon|spinner|loader)',
            r'\.(dialog|tooltip|popover|dropdown|select|checkbox|radio|toggle|switch)',
            r'\.(grid|list|item|row|col|column|flex|container|wrapper|layout)',
        ]
        comp_hits: set = set()
        for pat in component_patterns:
            for m in re.finditer(pat, css_text, re.IGNORECASE):
                comp_hits.add(m.group(1).lower())
        intelligence["component_hints"] = sorted(comp_hits)[:40]

        # General class-name vocabulary
        class_hits: set = set()
        for m in re.finditer(r'\.([a-z][a-z0-9_-]{3,30})\s*\{', css_text, re.IGNORECASE):
            class_hits.add(m.group(1).lower())
        intelligence["class_hints"] = sorted(class_hits)[:60]

        return intelligence

    # ------------------------------------------------------------------ #
    # NAVIGATION (HTML shell)
    # ------------------------------------------------------------------ #

    def _extract_navigation(self, soup: BeautifulSoup, base_url: str) -> dict:
        navigation: Dict[str, list] = {
            "internal_links": [],
            "external_links": [],
            "anchors": [],
            "mailto": [],
            "telephone": [],
            "downloads": [],
        }
        base_domain = urlparse(base_url).netloc
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(" ", strip=True)
            record = {"text": text, "href": href}
            if href.startswith("#"):
                navigation["anchors"].append(record)
            elif href.startswith("mailto:"):
                navigation["mailto"].append(record)
            elif href.startswith("tel:"):
                navigation["telephone"].append(record)
            elif href.lower().endswith(
                (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".zip")
            ):
                navigation["downloads"].append(record)
            else:
                absolute = urljoin(base_url, href)
                if urlparse(absolute).netloc == base_domain:
                    navigation["internal_links"].append(record)
                else:
                    navigation["external_links"].append(record)
        return navigation

    # ------------------------------------------------------------------ #
    # UI ELEMENTS (HTML shell — may be empty for SPAs)
    # ------------------------------------------------------------------ #

    def _extract_forms(self, soup: BeautifulSoup) -> list:
        forms = []
        for form in soup.find_all("form"):
            forms.append({
                "id": form.get("id"),
                "name": form.get("name"),
                "action": form.get("action"),
                "method": form.get("method", "GET").upper(),
                "autocomplete": form.get("autocomplete"),
                "enctype": form.get("enctype"),
                "novalidate": form.has_attr("novalidate"),
                "input_count": len(form.find_all("input")),
                "textarea_count": len(form.find_all("textarea")),
                "select_count": len(form.find_all("select")),
                "button_count": len(form.find_all("button")),
            })
        return forms

    def _extract_inputs(self, soup: BeautifulSoup) -> list:
        inputs = []
        for inp in soup.find_all("input"):
            inputs.append({
                "type": inp.get("type", "text"),
                "name": inp.get("name"),
                "id": inp.get("id"),
                "placeholder": inp.get("placeholder"),
                "value": inp.get("value"),
                "required": inp.has_attr("required"),
                "disabled": inp.has_attr("disabled"),
                "readonly": inp.has_attr("readonly"),
                "maxlength": inp.get("maxlength"),
                "minlength": inp.get("minlength"),
                "pattern": inp.get("pattern"),
                "autocomplete": inp.get("autocomplete"),
            })
        return inputs

    def _extract_buttons(self, soup: BeautifulSoup) -> list:
        buttons = []
        for btn in soup.find_all("button"):
            buttons.append({
                "text": btn.get_text(" ", strip=True),
                "type": btn.get("type"),
                "id": btn.get("id"),
                "class": btn.get("class"),
                "disabled": btn.has_attr("disabled"),
                "aria_label": btn.get("aria-label"),
                "onclick": btn.get("onclick"),
            })
        return buttons

    def _extract_images(self, soup: BeautifulSoup) -> list:
        images = []
        for img in soup.find_all("img"):
            images.append({
                "src": img.get("src"),
                "alt": img.get("alt"),
                "title": img.get("title"),
                "width": img.get("width"),
                "height": img.get("height"),
                "loading": img.get("loading"),
                "srcset": img.get("srcset"),
            })
        return images

    def _extract_tables(self, soup: BeautifulSoup) -> list:
        tables = []
        for table in soup.find_all("table"):
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            tables.append({
                "caption": (
                    table.caption.get_text(strip=True)
                    if table.caption else None
                ),
                "headers": headers,
                "rows": len(table.find_all("tr")),
                "thead": table.find("thead") is not None,
                "tbody": table.find("tbody") is not None,
                "tfoot": table.find("tfoot") is not None,
            })
        return tables

    def _extract_headings(self, soup: BeautifulSoup) -> dict:
        return {
            f"h{i}": [h.get_text(" ", strip=True) for h in soup.find_all(f"h{i}")]
            for i in range(1, 7)
        }

    def _extract_lists(self, soup: BeautifulSoup) -> dict:
        return {
            "unordered_lists": len(soup.find_all("ul")),
            "ordered_lists": len(soup.find_all("ol")),
            "description_lists": len(soup.find_all("dl")),
            "list_items": len(soup.find_all("li")),
        }

    # ------------------------------------------------------------------ #
    # ACCESSIBILITY
    # ------------------------------------------------------------------ #

    def _extract_accessibility(self, soup: BeautifulSoup) -> dict:
        accessibility: Dict[str, object] = {
            "images_with_alt": 0,
            "images_without_alt": 0,
            "aria_labels": 0,
            "labels": 0,
            "roles": [],
            "landmarks": [],
            "missing_form_labels": 0,
        }
        roles: set = set()
        landmarks: set = set()
        labelled_inputs: set = set()
        landmark_roles = {"banner", "navigation", "main", "contentinfo", "search"}

        for label in soup.find_all("label"):
            accessibility["labels"] = int(accessibility["labels"]) + 1  # type: ignore[arg-type]
            if label.get("for"):
                labelled_inputs.add(label.get("for"))

        for img in soup.find_all("img"):
            if img.get("alt") is not None:
                accessibility["images_with_alt"] = int(accessibility["images_with_alt"]) + 1  # type: ignore[arg-type]
            else:
                accessibility["images_without_alt"] = int(accessibility["images_without_alt"]) + 1  # type: ignore[arg-type]

        accessibility["aria_labels"] = len(soup.find_all(attrs={"aria-label": True}))

        for tag in soup.find_all(attrs={"role": True}):
            role = tag.get("role")
            roles.add(role)
            if role in landmark_roles:
                landmarks.add(role)

        for inp in soup.find_all("input"):
            inp_id = inp.get("id")
            if inp_id and inp_id not in labelled_inputs:
                accessibility["missing_form_labels"] = int(accessibility["missing_form_labels"]) + 1  # type: ignore[arg-type]

        accessibility["roles"]     = sorted(roles)
        accessibility["landmarks"] = sorted(landmarks)
        return accessibility

    # ------------------------------------------------------------------ #
    # STRUCTURED DATA
    # ------------------------------------------------------------------ #

    def _extract_structured_data(self, soup: BeautifulSoup) -> dict:
        structured: Dict[str, object] = {"json_ld": [], "microdata_items": 0}
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                structured["json_ld"].append(json.loads(script.string))  # type: ignore[union-attr]
            except Exception:
                structured["json_ld"].append(script.string)              # type: ignore[union-attr]
        structured["microdata_items"] = len(soup.find_all(attrs={"itemscope": True}))
        return structured

    # ------------------------------------------------------------------ #
    # SECURITY HEADERS
    # ------------------------------------------------------------------ #

    def _extract_security_headers(self, response: requests.Response) -> dict:
        h = response.headers
        return {
            "https": response.url.startswith("https://"),
            "content_security_policy": h.get("Content-Security-Policy"),
            "strict_transport_security": h.get("Strict-Transport-Security"),
            "x_frame_options": h.get("X-Frame-Options"),
            "x_content_type_options": h.get("X-Content-Type-Options"),
            "referrer_policy": h.get("Referrer-Policy"),
            "permissions_policy": h.get("Permissions-Policy"),
            "cache_control": h.get("Cache-Control"),
        }

    # ------------------------------------------------------------------ #
    # ASSETS
    # ------------------------------------------------------------------ #

    def _extract_assets(self, soup: BeautifulSoup) -> dict:
        assets: Dict[str, list] = {
            "pdf": [], "documents": [], "images": [],
            "videos": [], "audio": [], "fonts": [], "icons": [],
        }
        for a in soup.find_all("a", href=True):
            href  = a["href"]
            lower = href.lower()
            if lower.endswith(".pdf"):
                assets["pdf"].append(href)
            elif lower.endswith((".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx")):
                assets["documents"].append(href)
        for img in soup.find_all("img"):
            assets["images"].append(img.get("src"))
        for video in soup.find_all("video"):
            assets["videos"].append(video.get("src"))
        for audio in soup.find_all("audio"):
            assets["audio"].append(audio.get("src"))
        for link in soup.find_all("link"):
            href = link.get("href", "")
            rel  = " ".join(link.get("rel") or [])
            if "font" in href.lower():
                assets["fonts"].append(href)
            if "icon" in rel:
                assets["icons"].append(href)
        return assets

    # ------------------------------------------------------------------ #
    # PAGE STATISTICS
    # ------------------------------------------------------------------ #

    def _extract_statistics(self, soup: BeautifulSoup) -> dict:
        return {
            "links":       len(soup.find_all("a")),
            "forms":       len(soup.find_all("form")),
            "inputs":      len(soup.find_all("input")),
            "buttons":     len(soup.find_all("button")),
            "images":      len(soup.find_all("img")),
            "tables":      len(soup.find_all("table")),
            "scripts":     len(soup.find_all("script")),
            "stylesheets": len(soup.find_all("link", rel="stylesheet")),
            "headings":    sum(len(soup.find_all(f"h{i}")) for i in range(1, 7)),
        }

    # ------------------------------------------------------------------ #
    # CONTENT SUMMARY
    # ------------------------------------------------------------------ #

    def _extract_content_summary(self, soup: BeautifulSoup) -> dict:
        working = BeautifulSoup(str(soup), "html.parser")
        for tag in working(["script", "style", "noscript"]):
            tag.decompose()
        text = working.get_text(" ", strip=True)
        return {
            "preview":    text[:50_000],
            "characters": len(text),
            "words":      len(text.split()),
        }

    # ------------------------------------------------------------------ #
    # AUTHENTICATION (combined HTML + bundle)
    # ------------------------------------------------------------------ #

    def _detect_authentication(
        self,
        soup: BeautifulSoup,
        inputs: list,
        bundle_intelligence: Optional[dict],
    ) -> dict:
        page = str(soup).lower()

        password_fields = sum(1 for i in inputs if i["type"] == "password")
        observed_in_html = password_fields > 0

        # Bundle hints
        bundle_auth_hints: List[str] = []
        if bundle_intelligence:
            bundle_auth_hints = bundle_intelligence.get("auth_hints", [])  # type: ignore[assignment]

        auth_from_bundle = len(bundle_auth_hints) > 0

        # Qualify confidence
        if observed_in_html:
            confidence = _HIGH
            evidence   = _OBSERVED
        elif auth_from_bundle:
            confidence = _MEDIUM
            evidence   = _INFERRED
        else:
            confidence = _LOW
            evidence   = _UNKNOWN

        # SSO — only flag when strong keyword match (not HTTP headers)
        sso_signals = ["okta", "auth0", "azure ad", "openid connect", "single sign-on"]
        # Search only in title, meta, and body text (not full raw HTML to avoid header collisions)
        body_text = (soup.title.get_text() if soup.title else "") + page[:5000]
        sso_detected = any(w in body_text for w in sso_signals)
        # Also accept bundle hints
        if bundle_intelligence:
            sso_detected = sso_detected or any(
                h in ("okta", "auth0", "cognito") for h in bundle_auth_hints
            )

        return {
            "authentication_detected": observed_in_html or auth_from_bundle,
            "confidence": confidence,
            "evidence": evidence,
            "password_fields_in_html": password_fields,
            "auth_hints_in_bundle": bundle_auth_hints,
            "remember_me":     "remember me" in page,
            "forgot_password": "forgot password" in page,
            "signup":          "sign up" in page or "register" in page,
            "oauth":           "oauth" in page or (
                "oauth" in bundle_auth_hints if bundle_auth_hints else False
            ),
            "sso": sso_detected,
        }

    # ------------------------------------------------------------------ #
    # CRUD DETECTION (combined)
    # ------------------------------------------------------------------ #

    def _detect_crud(
        self,
        soup: BeautifulSoup,
        bundle_intelligence: Optional[dict],
    ) -> dict:
        page = str(soup).lower()
        actions = ["create", "add", "edit", "update", "delete", "remove", "save", "submit"]
        html_ops  = [a for a in actions if a in page]
        bundle_ops: List[str] = []
        if bundle_intelligence:
            bundle_ops = bundle_intelligence.get("crud_hints", [])  # type: ignore[assignment]
        all_ops = sorted(set(html_ops) | set(bundle_ops))
        return {
            "crud_detected": len(all_ops) > 0,
            "operations_in_html": html_ops,
            "operations_in_bundle": bundle_ops,
            "all_operations": all_ops,
        }

    # ------------------------------------------------------------------ #
    # BUSINESS DOMAIN ESTIMATION
    # ------------------------------------------------------------------ #

    _DOMAIN_KEYWORDS: Dict[str, List[str]] = {
        "E-Commerce":  ["cart", "checkout", "product", "shop", "order", "price"],
        "CRM":         ["lead", "pipeline", "opportunity", "deal", "crm"],
        "HRMS":        ["employee", "leave", "payroll", "attendance", "hr"],
        "Banking":     ["account", "balance", "transaction", "transfer", "bank"],
        "Healthcare":  ["patient", "doctor", "appointment", "clinic", "health"],
        "LMS":         ["course", "lesson", "quiz", "student", "enrollment"],
        "Project Mgmt":["task", "milestone", "sprint", "backlog", "kanban"],
        "Analytics":   ["dashboard", "chart", "report", "metric", "kpi"],
    }

    def _estimate_business_domain(
        self,
        soup: BeautifulSoup,
        bundle_intelligence: Optional[dict],
        css_intelligence: Optional[dict],
    ) -> dict:
        # Gather text from multiple sources for fairer scoring
        text_sources: List[str] = [
            soup.get_text(" ", strip=True).lower(),
        ]
        if bundle_intelligence:
            text_sources.append(
                " ".join(bundle_intelligence.get("routes_inferred", []))  # type: ignore[arg-type]
                + " "
                + " ".join(bundle_intelligence.get("page_modules", []))   # type: ignore[arg-type]
            )
        if css_intelligence:
            text_sources.append(
                " ".join(css_intelligence.get("page_hints", []))           # type: ignore[arg-type]
            )

        combined = " ".join(text_sources)

        scores: Dict[str, int] = {}
        for domain, keywords in self._DOMAIN_KEYWORDS.items():
            scores[domain] = sum(kw in combined for kw in keywords)

        best_score = max(scores.values())
        if best_score == 0:
            return {
                "domain": "Unknown",
                "confidence": _LOW,
                "evidence": _UNKNOWN,
                "scores": scores,
            }

        best_domain = max(scores, key=lambda d: scores[d])
        confidence  = _HIGH if best_score >= 3 else (_MEDIUM if best_score >= 2 else _LOW)
        return {
            "domain": best_domain,
            "confidence": confidence,
            "evidence": _INFERRED,
            "scores": scores,
        }

    # ------------------------------------------------------------------ #
    # PER-SECTION CONFIDENCE SCORING
    # ------------------------------------------------------------------ #

    def _calculate_section_confidence(
        self,
        rendering: dict,
        technologies: dict,
        metadata: dict,
        statistics: dict,
        bundle_intelligence: Optional[dict],
        css_intelligence: Optional[dict],
    ) -> dict:
        is_spa = rendering["architecture"] == "SPA"

        # Metadata section
        meta_score = min(100, 40 + len(metadata.get("standard", {})) * 5)

        # Technology section
        tech_score = 50
        if technologies["frontend"]:
            tech_score += 30
        if bundle_intelligence and bundle_intelligence.get("framework_hints"):
            tech_score += 20
        tech_score = min(100, tech_score)

        # UI / DOM section (low for SPAs because DOM isn't rendered)
        ui_score = 10 if is_spa and statistics["forms"] == 0 else 70

        # Bundle intelligence
        bundle_score = 0
        if bundle_intelligence:
            routes  = len(bundle_intelligence.get("routes_inferred", []))  # type: ignore[arg-type]
            api_eps = len(bundle_intelligence.get("api_endpoints_inferred", []))  # type: ignore[arg-type]
            bundle_score = min(100, 20 + routes * 2 + api_eps * 3)

        # Auth section
        auth_score = (
            90 if statistics["inputs"] > 0
            else (60 if bundle_intelligence and bundle_intelligence.get("auth_hints") else 20)
        )

        # Overall
        if is_spa:
            overall = int(
                meta_score   * 0.20
                + tech_score * 0.25
                + ui_score   * 0.10
                + bundle_score * 0.30
                + auth_score * 0.15
            )
        else:
            overall = int(
                meta_score   * 0.20
                + tech_score * 0.20
                + ui_score   * 0.35
                + bundle_score * 0.10
                + auth_score * 0.15
            )

        return {
            "overall": min(100, overall),
            "metadata":   meta_score,
            "technology": tech_score,
            "ui_dom":     ui_score,
            "bundle":     bundle_score,
            "auth":       auth_score,
        }

    # ------------------------------------------------------------------ #
    # COMPLEXITY
    # ------------------------------------------------------------------ #

    def _calculate_complexity(
        self,
        statistics: dict,
        bundle_intelligence: Optional[dict],
    ) -> str:
        score = (
            statistics["forms"]   * 10
            + statistics["tables"] * 10
            + statistics["buttons"]
            + statistics["inputs"]
            + statistics["scripts"] * 2
            + statistics["links"]
        )
        # For SPAs, supplement with bundle signals
        if bundle_intelligence:
            score += len(bundle_intelligence.get("routes_inferred", []))   * 5   # type: ignore[arg-type]
            score += len(bundle_intelligence.get("api_endpoints_inferred", [])) * 3  # type: ignore[arg-type]
            score += len(bundle_intelligence.get("page_modules", []))      * 4   # type: ignore[arg-type]

        if score < 60:
            return "Low"
        if score < 200:
            return "Medium"
        return "High"

    # ------------------------------------------------------------------ #
    # RECOMMENDATIONS
    # ------------------------------------------------------------------ #

    def _generate_recommendations(
        self,
        rendering: dict,
        accessibility: dict,
        security: dict,
        statistics: dict,
        authentication: dict,
        bundle_intelligence: Optional[dict],
    ) -> list:
        recs = []

        # Most important: rendering limitation
        if rendering["architecture"] == "SPA":
            recs.append(
                "[CRITICAL] SPA detected — HTML shell only. "
                "Static analysis is incomplete. "
                "Use a browser-rendering tool (Playwright/Selenium) to access the full DOM."
            )

        if bundle_intelligence:
            routes = bundle_intelligence.get("routes_inferred", [])
            if routes:
                recs.append(
                    f"[BUNDLE] {len(routes)} route(s) inferred from JS bundle. "  # type: ignore[arg-type]
                    "Use these as starting points for browser-based exploration."
                )
            api_eps = bundle_intelligence.get("api_endpoints_inferred", [])
            if api_eps:
                recs.append(
                    f"[BUNDLE] {len(api_eps)} API endpoint(s) inferred. "  # type: ignore[arg-type]
                    "Consider API-level testing in addition to UI testing."
                )

        if accessibility["images_without_alt"] > 0:
            recs.append("Add ALT attributes to images for accessibility.")
        if accessibility["missing_form_labels"] > 0:
            recs.append("Associate labels with form inputs.")

        if not security.get("content_security_policy"):
            recs.append("Content-Security-Policy header is missing.")
        if not security.get("strict_transport_security"):
            recs.append("Strict-Transport-Security (HSTS) header is missing.")

        if statistics["scripts"] > 25:
            recs.append("Large number of JavaScript files detected — consider auditing.")

        if authentication["authentication_detected"]:
            recs.append(
                "Authentication flow detected "
                f"({authentication['evidence']}). "
                "Include login/logout test scenarios."
            )

        if not recs:
            recs.append("No major issues detected during static exploration.")
        return recs

    # ------------------------------------------------------------------ #
    # INFERRED WORKFLOW
    # ------------------------------------------------------------------ #

    def _infer_workflow(
        self,
        bundle_intelligence: Optional[dict],
        css_intelligence: Optional[dict],
        authentication: dict,
    ) -> dict:
        """
        Reconstruct a plausible user workflow from inferred routes,
        CSS page hints, and auth signals.
        """
        steps: List[str] = []
        sources: List[str] = []

        # Auth entry point
        if authentication["authentication_detected"]:
            steps.append("Login")
            sources.append("auth_detection")

        # Routes from bundle
        route_hints: List[str] = []
        if bundle_intelligence:
            route_hints = [
                r for r in bundle_intelligence.get("routes_inferred", [])  # type: ignore[assignment]
                if r not in ("/", "/*", "*")
            ]

        # CSS page hints
        css_hints: List[str] = []
        if css_intelligence:
            css_hints = css_intelligence.get("page_hints", [])  # type: ignore[assignment]

        combined_hints = list({*route_hints, *css_hints})
        if combined_hints:
            sources.append("bundle_routes_and_css")
            for hint in sorted(combined_hints)[:10]:
                label = hint.strip("/").replace("-", " ").replace("_", " ").title()
                if label and label not in steps:
                    steps.append(label)

        if authentication.get("sso"):
            steps.insert(0, "SSO / Identity Provider Redirect")
            sources.append("sso_detection")

        if authentication.get("forgot_password"):
            steps.append("Password Recovery")

        if authentication.get("signup"):
            steps.append("User Registration")

        confidence = _HIGH if len(sources) >= 2 else (_MEDIUM if sources else _NONE)
        return {
            "inferred_steps": steps,
            "confidence": confidence,
            "sources": sources,
            "note": (
                "Workflow is inferred from static signals. "
                "Verify with browser rendering."
            ),
        }

    # ------------------------------------------------------------------ #
    # SUMMARY
    # ------------------------------------------------------------------ #

    def _generate_summary(
        self,
        page: dict,
        rendering: dict,
        technologies: dict,
        statistics: dict,
        domain: dict,
        complexity: str,
        confidence: dict,
        authentication: dict,
        bundle_intelligence: Optional[dict],
    ) -> dict:
        return {
            "title":               page["title"],
            "rendering_architecture": rendering["architecture"],
            "business_domain":     domain["domain"],
            "domain_confidence":   domain["confidence"],
            "frontend_frameworks": technologies["frontend"],
            "css_frameworks":      technologies["css_frameworks"],
            "javascript_libraries": technologies["javascript_libraries"],
            "state_management":    (
                bundle_intelligence.get("state_management", [])
                if bundle_intelligence else []
            ),
            "authentication":      authentication["authentication_detected"],
            "auth_evidence":       authentication["evidence"],
            "complexity":          complexity,
            "overall_confidence":  confidence["overall"],
            "statistics":          statistics,
            "spa_warning": (
                "HTML shell only — DOM unavailable without JavaScript execution."
                if rendering["architecture"] == "SPA"
                else None
            ),
        }

    # ------------------------------------------------------------------ #
    # RUN
    # ------------------------------------------------------------------ #

    def _run(self, url: str) -> str:
        self._log("=" * 80)
        self._log("Static Application Intelligence Engine — Starting")
        self._log(url)

        try:
            response, soup = self._fetch_page(url)

            # ---- Phase 1: HTML shell analysis ----
            http        = self._extract_http_info(response)
            page        = self._extract_page_information(soup, response)
            metadata    = self._extract_meta_tags(soup)
            scripts     = self._extract_scripts(soup)
            stylesheets = self._extract_stylesheets(soup)
            technologies = self._detect_technologies(soup)
            navigation  = self._extract_navigation(soup, response.url)
            forms       = self._extract_forms(soup)
            inputs      = self._extract_inputs(soup)
            buttons     = self._extract_buttons(soup)
            images      = self._extract_images(soup)
            tables      = self._extract_tables(soup)
            headings    = self._extract_headings(soup)
            lists       = self._extract_lists(soup)
            accessibility    = self._extract_accessibility(soup)
            structured_data  = self._extract_structured_data(soup)
            security    = self._extract_security_headers(response)
            assets      = self._extract_assets(soup)
            statistics  = self._extract_statistics(soup)
            content     = self._extract_content_summary(soup)
            rendering   = self._detect_rendering_architecture(soup, response, scripts)

            # ---- Phase 2: JS bundle deep analysis ----
            bundle_intelligence: Optional[dict] = None
            bundle_url = self._pick_primary_bundle(
                scripts.get("external", []),  # type: ignore[arg-type]
                response.url,
            )
            if bundle_url:
                self._log(f"Analysing JS bundle: {bundle_url}")
                bundle_text = self._fetch_text_asset(
                    bundle_url, _JS_BUNDLE_MAX_BYTES, "JS bundle"
                )
                if bundle_text:
                    bundle_intelligence = self._analyze_js_bundle(bundle_text, response.url)
                    # Extend technology detection with bundle findings
                    for fw in bundle_intelligence.get("framework_hints", []):
                        if fw not in technologies["frontend"]:
                            technologies["frontend"].append(fw)

            # ---- Phase 3: CSS semantic analysis ----
            css_intelligence: Optional[dict] = None
            css_urls: List[str] = stylesheets.get("external", [])  # type: ignore[assignment]
            if css_urls:
                primary_css_url = urljoin(response.url, css_urls[0])
                self._log(f"Analysing CSS: {primary_css_url}")
                css_text = self._fetch_text_asset(
                    primary_css_url, _CSS_MAX_BYTES, "CSS"
                )
                if css_text:
                    css_intelligence = self._analyze_css(css_text)

            # ---- Phase 4: Higher-order analysis ----
            authentication = self._detect_authentication(soup, inputs, bundle_intelligence)
            crud           = self._detect_crud(soup, bundle_intelligence)
            domain         = self._estimate_business_domain(soup, bundle_intelligence, css_intelligence)
            complexity     = self._calculate_complexity(statistics, bundle_intelligence)
            confidence     = self._calculate_section_confidence(
                rendering, technologies, metadata, statistics,
                bundle_intelligence, css_intelligence,
            )
            workflow       = self._infer_workflow(bundle_intelligence, css_intelligence, authentication)
            recommendations = self._generate_recommendations(
                rendering, accessibility, security, statistics,
                authentication, bundle_intelligence,
            )
            summary = self._generate_summary(
                page, rendering, technologies, statistics, domain,
                complexity, confidence, authentication, bundle_intelligence,
            )

            result = {
                "metadata": {
                    "tool":      self.name,
                    "version":   "3.0",
                    "timestamp": datetime.utcnow().isoformat(),
                    "status":    "SUCCESS",
                    "analysed_url": response.url,
                },
                "summary":     summary,
                "http":        http,
                "rendering":   rendering,
                "page":        page,
                "meta_tags":   metadata,
                "technology":  technologies,
                "security":    security,
                "navigation":  navigation,
                "ui": {
                    "note": (
                        "UI elements below reflect the static HTML shell. "
                        "For SPA applications counts may be zero — "
                        "see bundle_intelligence for inferred UI signals."
                        if rendering["architecture"] == "SPA" else ""
                    ),
                    "forms":   forms,
                    "inputs":  inputs,
                    "buttons": buttons,
                    "tables":  tables,
                    "images":  images,
                    "headings": headings,
                    "lists":   lists,
                },
                "scripts":           scripts,
                "stylesheets":       stylesheets,
                "assets":            assets,
                "accessibility":     accessibility,
                "structured_data":   structured_data,
                "statistics":        statistics,
                "content":           content,
                "authentication":    authentication,
                "crud":              crud,
                "workflow":          workflow,
                "bundle_intelligence": bundle_intelligence,
                "css_intelligence":  css_intelligence,
                "business_domain":   domain,
                "complexity":        complexity,
                "confidence":        confidence,
                "recommendations":   recommendations,
            }

            self._log("Static Application Intelligence Engine — Completed")
            return json.dumps(result, indent=2, ensure_ascii=False)

        except Exception as ex:
            logging.getLogger(self.name).exception("Exploration Failed")
            return json.dumps(
                {
                    "metadata": {
                        "tool":      self.name,
                        "version":   "3.0",
                        "timestamp": datetime.utcnow().isoformat(),
                        "status":    "FAILURE",
                    },
                    "error": {
                        "type":    type(ex).__name__,
                        "message": str(ex),
                    },
                },
                indent=2,
            )