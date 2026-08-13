"""
Quick verification test for BrowserAutomationTool (remote worker client).
This is NOT a unit test - just a sanity check that the code loads and structure is correct.
"""

import importlib.util
import json
import sys
from pathlib import Path

TOOL_PATH = Path(__file__).parent / "browser-automation-tool.py"


def _load_tool_module():
    spec = importlib.util.spec_from_file_location("browser_automation_tool", TOOL_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {TOOL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["browser_automation_tool"] = module
    spec.loader.exec_module(module)
    return module


try:
    mod = _load_tool_module()
    BrowserAutomationTool = mod.BrowserAutomationTool
    BrowserAutomationToolSchema = mod.BrowserAutomationToolSchema
    print("OK: Successfully imported BrowserAutomationTool")
except Exception as e:
    print(f"FAIL: Import failed: {e}")
    sys.exit(1)

# Verify schema has remote-worker fields
try:
    schema = BrowserAutomationToolSchema(
        url="https://example.com",
        session_id="run-1",
        action="Navigate",
        ignore_https_errors=True,
    )
    assert schema.ignore_https_errors is True
    assert schema.session_id == "run-1"
    assert schema.action == "Navigate"
    print("OK: Schema has session_id/action/ignore_https_errors fields")
except Exception as e:
    print(f"FAIL: Schema validation failed: {e}")
    sys.exit(1)

# Verify tool instantiation
try:
    tool = BrowserAutomationTool()
    print("OK: Tool instantiated successfully")
except Exception as e:
    print(f"FAIL: Tool instantiation failed: {e}")
    sys.exit(1)

# Verify remote-worker helpers exist
try:
    assert hasattr(tool, "_post_json")
    assert hasattr(tool, "_worker_base_url")
    assert not hasattr(tool, "_check_browser_installed")
    print("OK: Tool exposes remote-worker client methods (no local Playwright)")
except Exception as e:
    print(f"FAIL: Method check failed: {e}")
    sys.exit(1)

# Verify clear error when worker URL is missing
try:
    raw = tool._run(url="https://example.com")
    data = json.loads(raw)
    assert data.get("error") is True
    assert data.get("code") == "WORKER_URL_NOT_CONFIGURED"
    print("OK: Missing BROWSER_WORKER_URL returns WORKER_URL_NOT_CONFIGURED")
except Exception as e:
    print(f"FAIL: Missing-worker error check failed: {e}")
    sys.exit(1)

# Verify tool description/schema linkage
try:
    assert tool.args_schema == BrowserAutomationToolSchema
    assert "remote" in tool.description.lower() or "worker" in tool.description.lower()
    print("OK: Tool schema correctly linked and description mentions remote worker")
except Exception as e:
    print(f"FAIL: Schema linkage failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("All structural checks passed!")
print("=" * 60)
print("\nNote: This tool does NOT run Playwright in-process.")
print("Set BROWSER_WORKER_URL to a running Playwright worker before functional use.")
