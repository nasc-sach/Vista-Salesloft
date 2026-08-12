"""
Quick verification test for BrowserAutomationTool fixes.
This is NOT a unit test - just a sanity check that the code loads and structure is correct.
"""

import json
import sys
from pathlib import Path

# Add tool directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from browser_automation_tool import BrowserAutomationTool, BrowserAutomationToolSchema
    print("✓ Successfully imported BrowserAutomationTool")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Verify schema has new field
try:
    schema = BrowserAutomationToolSchema(
        url="https://example.com",
        ignore_https_errors=True
    )
    assert schema.ignore_https_errors == True
    print("✓ Schema has ignore_https_errors field")
except Exception as e:
    print(f"✗ Schema validation failed: {e}")
    sys.exit(1)

# Verify tool instantiation
try:
    tool = BrowserAutomationTool()
    print("✓ Tool instantiated successfully")
except Exception as e:
    print(f"✗ Tool instantiation failed: {e}")
    sys.exit(1)

# Verify new method exists
try:
    assert hasattr(tool, '_check_browser_installed')
    print("✓ Tool has _check_browser_installed method")
except Exception as e:
    print(f"✗ Method check failed: {e}")
    sys.exit(1)

# Verify tool description mentions new functionality
try:
    assert tool.args_schema == BrowserAutomationToolSchema
    print("✓ Tool schema correctly linked")
except Exception as e:
    print(f"✗ Schema linkage failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("All structural checks passed!")
print("="*60)
print("\nNote: This test only verifies code structure.")
print("To test actual functionality, you need Playwright installed.")
print("\nQuick functional test:")
print("  python -c \"from browser_automation_tool import BrowserAutomationTool; t = BrowserAutomationTool(); print(t._run('https://example.com'))\"")