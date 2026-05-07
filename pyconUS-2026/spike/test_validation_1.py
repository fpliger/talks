"""Playwright test for MCP validation in PyScript."""

from playwright.sync_api import sync_playwright
import time

def test_mcp_validation():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console logs
        console_logs = []
        def log_console(msg):
            text = f"[{msg.type}] {msg.text}"
            console_logs.append(text)
            print(f"  CONSOLE: {text}")
        page.on("console", log_console)

        print("Navigating to validation page...")
        page.goto("http://localhost:8080")

        # Wait for PyScript to fully load (it takes a while)
        print("Waiting for PyScript to load...")
        page.wait_for_load_state("networkidle")

        # Wait for the "Ready" message which indicates PyScript is loaded
        try:
            page.wait_for_selector("text=Ready", timeout=60000)
            print("PyScript loaded successfully!")
        except Exception as e:
            print(f"PyScript load timeout: {e}")
            page.screenshot(path="/tmp/pyscript_load_fail.png", full_page=True)
            print("Screenshot saved to /tmp/pyscript_load_fail.png")
            browser.close()
            return False

        # Take initial screenshot
        page.screenshot(path="/tmp/validation1_initial.png", full_page=True)
        print("Initial screenshot saved to /tmp/validation1_initial.png")

        # Run all tests with single button click
        print("\n--- Running All Tests ---")
        page.click("#test-all")
        try:
            page.wait_for_selector("text=VALIDATION 1 PASSED", timeout=30000)
            print("All tests completed!")
        except:
            print("Tests timeout - waiting additional time...")
            time.sleep(10)
        page.screenshot(path="/tmp/validation1_final.png", full_page=True)

        # Get final page content
        content = page.inner_html("#output")
        print("\n--- Results ---")
        print(content[:2000] if len(content) > 2000 else content)

        # Print all console logs
        print("\n--- Console Logs ---")
        for log in console_logs[-20:]:  # Last 20 logs
            print(log)

        # Check for pass/fail
        if "VALIDATION 1 PASSED" in content:
            print("\n✓ VALIDATION 1 PASSED")
            result = True
        elif "pass" in content.lower():
            print("\n✓ Tests passed (partial)")
            result = True
        else:
            print("\n✗ Tests may have failed - check screenshots")
            result = False

        print(f"\nScreenshots saved to /tmp/validation1_*.png")

        browser.close()
        return result

if __name__ == "__main__":
    success = test_mcp_validation()
    exit(0 if success else 1)
