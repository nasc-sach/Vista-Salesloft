"""
Example usage and integration tests for BrowserAutomationTool.

This file demonstrates how to use the BrowserAutomationTool in various scenarios.
Run with: python examples_browser_automation_tool.py
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from browser_automation_tool import BrowserAutomationTool


def example_1_basic_usage():
    """Example 1: Basic SPA exploration"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic React SPA Exploration")
    print("="*70)
    
    tool = BrowserAutomationTool()
    
    # Explore a public React SPA
    result_json = tool._run(
        url="https://react.dev",
        wait_for_selector="#root",
        capture_network=True,
        take_screenshot=True,
        headless=True
    )
    
    result = json.loads(result_json)
    
    if not result.get("error"):
        print(f"\n✅ Successfully explored: {result['url']}")
        print(f"   Framework: {result['rendering']['framework']}")
        print(f"   Architecture: {result['rendering']['architecture']}")
        print(f"   Execution Time: {result['execution_time_ms']}ms")
        print(f"   API Calls Captured: {len(result['network']['api_calls'])}")
        print(f"   Screenshot: {result['screenshot_path']}")
        
        print(f"\n📊 Network Summary:")
        for resource_type, count in result['network']['resource_summary'].items():
            print(f"   {resource_type}: {count}")
        
        print(f"\n💡 Recommendations:")
        for rec in result['recommendations'][:3]:
            print(f"   - {rec}")
    else:
        print(f"\n❌ Error: {result['message']}")
    
    return result


def example_2_with_authentication():
    """Example 2: Authentication flow (mock example)"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Authentication Flow")
    print("="*70)
    
    tool = BrowserAutomationTool()
    
    # This is a mock example - replace with actual test site credentials
    print("\n⚠️  This example requires valid test credentials")
    print("   Modify authenticate parameter with real login URL and credentials\n")
    
    example_auth_config = {
        "login_url": "https://example.com/login",
        "username": "test@example.com",
        "password": "testpassword123"
    }
    
    print(f"Example auth config structure:")
    print(json.dumps(example_auth_config, indent=2))
    
    # Uncomment to test with real credentials:
    # result_json = tool._run(
    #     url="https://example.com/dashboard",
    #     authenticate=example_auth_config,
    #     wait_for_selector=".dashboard-loaded",
    #     capture_network=True,
    #     take_screenshot=True
    # )
    # 
    # result = json.loads(result_json)
    # if not result.get("error"):
    #     print(f"✅ Logged in: {result['authentication']['logged_in']}")
    #     print(f"   Auth Evidence: {result['authentication']['evidence']}")


def example_3_network_analysis():
    """Example 3: Network traffic and API discovery"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Network Traffic and API Discovery")
    print("="*70)
    
    tool = BrowserAutomationTool()
    
    # Explore site with focus on network traffic
    result_json = tool._run(
        url="https://jsonplaceholder.typicode.com",  # Public API demo site
        capture_network=True,
        take_screenshot=False,  # Skip screenshot for faster execution
        wait_timeout=15000
    )
    
    result = json.loads(result_json)
    
    if not result.get("error"):
        print(f"\n✅ Network Analysis Complete")
        print(f"   Total Requests: {result['network']['total_requests']}")
        print(f"   API Calls Captured: {len(result['network']['api_calls'])}")
        
        print(f"\n🌐 API Endpoints Discovered:")
        for api_call in result['network']['api_calls'][:5]:
            print(f"   {api_call['method']} {api_call['endpoint']}")
            print(f"      └─ Status: {api_call['status']}, Type: {api_call['content_type']}")
        
        if len(result['network']['api_calls']) > 5:
            print(f"   ... and {len(result['network']['api_calls']) - 5} more")
    
    return result


def example_4_dom_extraction():
    """Example 4: DOM element extraction (forms, buttons, links)"""
    print("\n" + "="*70)
    print("EXAMPLE 4: DOM Element Extraction")
    print("="*70)
    
    tool = BrowserAutomationTool()
    
    result_json = tool._run(
        url="https://www.wikipedia.org",
        wait_for_selector="#searchInput",
        capture_network=False,
        take_screenshot=False
    )
    
    result = json.loads(result_json)
    
    if not result.get("error"):
        dom = result['dom']
        
        print(f"\n✅ DOM Extraction Complete")
        print(f"   Title: {dom['title']}")
        print(f"   Description: {dom['meta'].get('description', 'N/A')[:80]}...")
        
        print(f"\n📝 Forms Found: {len(dom['forms'])}")
        for i, form in enumerate(dom['forms'][:2], 1):
            print(f"   Form {i}:")
            print(f"      Action: {form['action'] or 'N/A'}")
            print(f"      Method: {form['method']}")
            print(f"      Inputs: {len(form['inputs'])}")
            for inp in form['inputs'][:3]:
                print(f"         - {inp['type']}: {inp['name']} (required: {inp['required']})")
        
        print(f"\n🔘 Interactive Elements:")
        print(f"   Buttons: {len(dom['interactive_elements']['buttons'])}")
        print(f"   Links: {len(dom['interactive_elements']['links'])}")
        
        print(f"\n🧭 Navigation:")
        nav = dom['navigation']
        print(f"   Nav Elements: {len(nav['nav_elements'])}")
        print(f"   Internal Links: {len(nav['internal_links'])}")
        print(f"   External Links: {len(nav['external_links'])}")
    
    return result


def example_5_crewai_integration():
    """Example 5: CrewAI agent integration pattern"""
    print("\n" + "="*70)
    print("EXAMPLE 5: CrewAI Agent Integration Pattern")
    print("="*70)
    
    print("""
    To integrate BrowserAutomationTool with CrewAI agents:
    
    ```python
    from crewai import Agent, Task, Crew
    from browser_automation_tool import BrowserAutomationTool
    
    # 1. Create agent with the tool
    explorer_agent = Agent(
        role="Web Application Security Analyst",
        goal="Analyze web applications for security vulnerabilities",
        backstory="Expert in web security, browser automation, and penetration testing",
        tools=[BrowserAutomationTool()],
        verbose=True
    )
    
    # 2. Create exploration task
    task = Task(
        description='''
        Explore the application at {url} and:
        1. Identify the framework (React/Vue/Angular)
        2. Extract all forms and input validation patterns
        3. Capture API endpoints and authentication requirements
        4. Document navigation structure and user flows
        5. Take screenshots of key pages
        
        Provide a comprehensive security assessment report.
        ''',
        agent=explorer_agent,
        expected_output="JSON report with findings and security recommendations"
    )
    
    # 3. Execute
    crew = Crew(
        agents=[explorer_agent],
        tasks=[task],
        verbose=True
    )
    
    result = crew.kickoff(inputs={"url": "https://example.com"})
    ```
    
    The agent will automatically invoke BrowserAutomationTool._run() with appropriate
    parameters based on the task description.
    """)


def example_6_error_handling():
    """Example 6: Error handling patterns"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Error Handling")
    print("="*70)
    
    tool = BrowserAutomationTool()
    
    # Test with invalid URL
    print("\n🧪 Testing with invalid URL...")
    result_json = tool._run(
        url="https://this-domain-definitely-does-not-exist-12345.com",
        wait_timeout=5000
    )
    
    result = json.loads(result_json)
    
    if result.get("error"):
        print(f"\n✅ Error handled gracefully:")
        print(f"   Code: {result['code']}")
        print(f"   Message: {result['message'][:100]}...")
        print(f"   Tool: {result['tool']}")
        
        print("\n💡 In production, handle errors like this:")
        print("""
        result = json.loads(tool._run(url=target_url))
        
        if result.get("error"):
            if result["code"] == "PLAYWRIGHT_NOT_INSTALLED":
                # Handle missing dependency
                install_playwright()
            elif result["code"] == "BROWSER_AUTOMATION_ERROR":
                # Handle automation failure (timeout, navigation error, etc.)
                log_error(result["message"])
                fallback_to_static_analysis()
        else:
            # Process successful result
            analyze_findings(result)
        """)


def example_7_performance_comparison():
    """Example 7: Performance comparison with static analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Performance Comparison")
    print("="*70)
    
    print("""
    Decision Flow: When to use BrowserAutomationTool vs BrowserExplorer
    
    1. START with BrowserExplorer (fast, lightweight):
       - Static HTML analysis
       - Quick architecture detection
       - ~1-3 seconds execution time
    
    2. ESCALATE to BrowserAutomationTool if:
       - SPA architecture detected (React/Vue/Angular)
       - Minimal initial HTML content
       - Authentication required
       - Dynamic forms/inputs loaded via JS
       - Network traffic analysis needed
    
    3. USE BOTH in sequence for comprehensive analysis:
       
       Phase 1: BrowserExplorer (static analysis)
       └─ If SPA detected → Phase 2: BrowserAutomationTool (dynamic analysis)
       
    Example execution times:
    - BrowserExplorer: ~1.5s (static parsing)
    - BrowserAutomationTool: ~4-8s (browser automation)
    - Combined approach: ~5.5-9.5s (comprehensive)
    """)


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("BrowserAutomationTool - Usage Examples")
    print("="*70)
    
    print("\n📚 Available Examples:")
    print("   1. Basic React SPA Exploration")
    print("   2. Authentication Flow")
    print("   3. Network Traffic and API Discovery")
    print("   4. DOM Element Extraction")
    print("   5. CrewAI Agent Integration")
    print("   6. Error Handling")
    print("   7. Performance Comparison")
    
    # Run examples that don't require external dependencies
    try:
        example_1_basic_usage()
    except Exception as e:
        print(f"\n❌ Example 1 failed: {e}")
    
    example_2_with_authentication()
    
    try:
        example_3_network_analysis()
    except Exception as e:
        print(f"\n❌ Example 3 failed: {e}")
    
    try:
        example_4_dom_extraction()
    except Exception as e:
        print(f"\n❌ Example 4 failed: {e}")
    
    example_5_crewai_integration()
    example_6_error_handling()
    example_7_performance_comparison()
    
    print("\n" + "="*70)
    print("✅ Examples Complete")
    print("="*70)


if __name__ == "__main__":
    main()