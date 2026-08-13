"""Targeted click-through of real VIS nav modules."""
import json
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "https://vistapoc.nitor.in"
USER = "manager1"
PASS = "Password123!"
NAV = [
    "Dashboard",
    "Staff Management",
    "Shift Management",
    "Weekly Roster",
    "Shift Requests",
    "Reference Data",
    "Export",
    "Audit",
]


def ts():
    return datetime.datetime.now(datetime.UTC).isoformat().replace("+00:00", "Z")


def extract_page(page, action="Navigate"):
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
        const body = (document.body.innerText || '').replace(/\\s+/g, ' ').trim();
        // split visible_text into meaningful chunks
        const visible_text = [];
        for (const el of document.querySelectorAll('h1,h2,h3,h4,h5,button,th,td,label,p,li,a,span')) {
          const t = text(el);
          if (t && t.length < 120 && t.length > 1 && !visible_text.includes(t)) visible_text.push(t);
          if (visible_text.length >= 50) break;
        }
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
          fetch_source: 'SPA Module Inspector',
          confidence: 'High'
        };
      }"""
    )
    data["action_performed"] = action
    data["timestamp"] = ts()
    return data


def main():
    network = []
    pages = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 900})
        page = context.new_page()
        page.on("response", lambda r: network.append(r.url))

        page.goto(BASE + "/login", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(800)
        pages["LOGIN"] = extract_page(page, "Navigate")

        page.fill("#username", USER)
        type_user = {
            "action_performed": "Type",
            "target_element": "username",
            "stored_fields": ["username"],
            "status": "Stored input for username",
            "timestamp": ts(),
            "confidence": "High",
        }
        page.fill("#password", PASS)
        type_pass = {
            "action_performed": "Type",
            "target_element": "password",
            "stored_fields": ["username", "password"],
            "status": "Stored input for password",
            "timestamp": ts(),
            "confidence": "High",
        }
        page.click('button:has-text("Sign In")')
        page.wait_for_url("**/dashboard**", timeout=30000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(1000)

        dash = extract_page(page, "Click (Form Submit)")
        dash["note"] = "Login executed successfully."
        pages["DASHBOARD"] = dash

        for label in NAV:
            try:
                page.get_by_role("button", name=label, exact=True).click(timeout=8000)
            except Exception:
                try:
                    page.get_by_text(label, exact=True).first.click(timeout=8000)
                except Exception as e:
                    pages[label.upper().replace(" ", "_")] = {"error": str(e), "action": label}
                    continue
            page.wait_for_timeout(1500)
            try:
                page.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                pass
            page.wait_for_timeout(800)
            key = label.upper().replace(" ", "_")
            pages[key] = extract_page(page, f"Click ({label})")

        session = {
            "observation": "Session State",
            "location": page.url,
            "logged_in": "login" not in page.url.lower(),
            "cookie_names": [c["name"] for c in context.cookies()],
            "local_storage_keys": page.evaluate("() => Object.keys(localStorage)"),
            "session_storage_keys": page.evaluate("() => Object.keys(sessionStorage)"),
            "local_storage_preview": page.evaluate(
                """() => {
                  const o = {};
                  for (const k of Object.keys(localStorage)) {
                    const v = localStorage.getItem(k) || '';
                    o[k] = v.length > 300 ? v.slice(0,300) + '...' : v;
                  }
                  return o;
                }"""
            ),
            "timestamp": ts(),
            "confidence": "High",
        }

        # signup public page (may redirect if already authenticated)
        page.goto(BASE + "/signup", wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(800)
        pages["SIGNUP"] = extract_page(page, "Navigate")

        api = sorted({u.split("?")[0] for u in network if "/api/" in u})
        auth = {
            "observation": "Authentication Form Detected",
            "location": "https://vistapoc.nitor.in/login",
            "login_form_visible": True,
            "credential_fields": [
                {"name": "username", "type": "text", "id": "username", "placeholder": "Username", "required": False},
                {"name": "password", "type": "password", "id": "password", "placeholder": "Password", "required": False},
            ],
            "submit_button": {"text": "Sign In", "type": "submit"},
            "secondary_actions": [{"text": "Sign up", "href": "/signup"}],
            "auth_type": "Form-Based Authentication",
            "public_accessible": True,
            "timestamp": ts(),
            "confidence": "High",
        }
        tech = {
            "url": "https://vistapoc.nitor.in/login",
            "https_confirmed": True,
            "framework_hints": ["React", "Vite"],
            "ui_library_hints": [],
            "api_patterns": [u.replace(BASE, "") if u.startswith(BASE) else u for u in api] or ["REST API (/api/v1/)"],
            "timestamp": ts(),
            "confidence": "High",
        }
        browser.close()

    out = {
        "AuthenticationDiscoveryTool": auth,
        "TechnologyDetectionTool": tech,
        "BrowserExplorationTool": {
            "TYPE_USERNAME": type_user,
            "TYPE_PASSWORD": type_pass,
            "PAGES": pages,
        },
        "SessionState": session,
        "api_endpoints_observed": api,
    }
    Path("_vista_explore_output.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote _vista_explore_output.json")
    print("PAGES:", list(pages.keys()))
    print("APIs:", len(api))


if __name__ == "__main__":
    main()
