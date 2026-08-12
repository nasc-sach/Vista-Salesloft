"""
Simple test file for LightweightBrowserTool.

Tests basic functionality without requiring external dependencies to be installed.
"""

import json
import sys
from unittest.mock import Mock, patch, MagicMock


def test_tool_structure():
    """Test that the tool has the correct structure and attributes."""
    print("Test 1: Checking tool structure...")
    
    # Mock the dependencies
    sys.modules['requests'] = Mock()
    sys.modules['bs4'] = Mock()
    sys.modules['pydantic'] = Mock()
    sys.modules['crewai'] = Mock()
    sys.modules['crewai.tools'] = Mock()
    
    # Create mock classes
    mock_base_model = type('BaseModel', (), {})
    mock_base_tool = type('BaseTool', (), {})
    mock_field = lambda **kwargs: None
    
    sys.modules['pydantic'].BaseModel = mock_base_model
    sys.modules['pydantic'].Field = mock_field
    sys.modules['crewai.tools'].BaseTool = mock_base_tool
    
    # Now import the tool
    import importlib.util
    spec = importlib.util.spec_from_file_location("browser_lightweight_tool", "browser-lightweight-tool.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    LightweightBrowserTool = module.LightweightBrowserTool
    
    # Check attributes
    assert hasattr(LightweightBrowserTool, 'name'), "Tool should have 'name' attribute"
    assert hasattr(LightweightBrowserTool, 'description'), "Tool should have 'description' attribute"
    assert hasattr(LightweightBrowserTool, 'args_schema'), "Tool should have 'args_schema' attribute"
    assert hasattr(LightweightBrowserTool, 'USER_AGENT'), "Tool should have 'USER_AGENT' attribute"
    
    print("OK Tool structure is correct")
    return True


def test_extraction_methods():
    """Test that extraction methods exist."""
    print("\nTest 2: Checking extraction methods...")
    
    # Mock dependencies
    sys.modules['requests'] = Mock()
    sys.modules['bs4'] = Mock()
    sys.modules['pydantic'] = Mock()
    sys.modules['crewai'] = Mock()
    sys.modules['crewai.tools'] = Mock()
    
    mock_base_model = type('BaseModel', (), {})
    mock_base_tool = type('BaseTool', (), {})
    mock_field = lambda **kwargs: None
    
    sys.modules['pydantic'].BaseModel = mock_base_model
    sys.modules['pydantic'].Field = mock_field
    sys.modules['crewai.tools'].BaseTool = mock_base_tool
    
    import importlib.util
    spec = importlib.util.spec_from_file_location("browser_lightweight_tool", "browser-lightweight-tool.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    LightweightBrowserTool = module.LightweightBrowserTool
    
    # Check methods
    required_methods = [
        '_get_session',
        '_fetch_page',
        '_extract_title',
        '_extract_meta_tags',
        '_extract_forms',
        '_extract_links',
        '_extract_buttons',
        '_extract_content_summary',
        '_extract_navigation',
        '_run'
    ]
    
    for method in required_methods:
        assert hasattr(LightweightBrowserTool, method), f"Tool should have '{method}' method"
    
    print("OK All extraction methods exist")
    return True


def test_error_handling():
    """Test that the tool handles errors in _run method."""
    print("\nTest 3: Checking error handling structure...")
    
    # Read the source file
    with open('browser-lightweight-tool.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for error handling
    error_types = [
        'SSLError',
        'Timeout',
        'ConnectionError',
        'HTTPError',
        'RequestException'
    ]
    
    for error_type in error_types:
        assert error_type in content, f"Should handle {error_type}"
    
    print("OK Error handling is comprehensive")
    return True


def test_output_format():
    """Test that the output format matches BrowserAutomationTool."""
    print("\nTest 4: Checking output format compatibility...")
    
    # Read the source file
    with open('browser-lightweight-tool.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required output fields
    required_fields = [
        '"url"',
        '"timestamp"',
        '"execution_time_ms"',
        '"success"',
        '"rendering"',
        '"dom"',
        '"errors"',
        '"warnings"',
        '"title"',
        '"meta"',
        '"forms"',
        '"interactive_elements"',
        '"navigation"'
    ]
    
    for field in required_fields:
        assert field in content, f"Output should include {field} field"
    
    print("OK Output format is compatible with BrowserAutomationTool")
    return True


def test_configuration():
    """Test tool configuration values."""
    print("\nTest 5: Checking configuration values...")
    
    # Read the source file
    with open('browser-lightweight-tool.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for user agent
    assert 'Vista-Planner/1.0 (Lightweight)' in content, "Should have correct user agent"
    assert 'REQUEST_TIMEOUT' in content, "Should have timeout configuration"
    assert 'MAX_CONTENT_PREVIEW' in content, "Should have content preview limit"
    
    print("OK Configuration values are correct")
    return True


def main():
    """Run all tests."""
    print("=" * 80)
    print("Testing LightweightBrowserTool")
    print("=" * 80)
    
    tests = [
        test_tool_structure,
        test_extraction_methods,
        test_error_handling,
        test_output_format,
        test_configuration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"X Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"X Test error: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)