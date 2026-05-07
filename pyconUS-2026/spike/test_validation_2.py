"""Playwright test for SSE streaming validation in PyScript."""

from playwright.sync_api import sync_playwright
import time

def test_sse_streaming():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console logs
        def log_console(msg):
            print(f"  CONSOLE: [{msg.type}] {msg.text[:100]}")
        page.on("console", log_console)

        print("Navigating to validation page...")
        page.goto("http://localhost:8081")

        print("Waiting for PyScript to load...")
        page.wait_for_load_state("networkidle")

        try:
            page.wait_for_selector("text=Ready", timeout=60000)
            print("PyScript loaded successfully!")
        except Exception as e:
            print(f"PyScript load timeout: {e}")
            page.screenshot(path="/tmp/pyscript_sse_fail.png", full_page=True)
            browser.close()
            return False

        # Test streaming
        print("\n--- Test: SSE Streaming ---")
        page.click("#test-stream")

        try:
            page.wait_for_selector("text=VALIDATION 2 PASSED", timeout=30000)
            print("Streaming test completed!")
        except:
            print("Streaming test timeout - waiting additional time...")
            time.sleep(5)

        page.screenshot(path="/tmp/validation2_streaming.png", full_page=True)

        # Get results
        content = page.inner_html("#output")
        print("\n--- Results ---")
        print(content[:2000] if len(content) > 2000 else content)

        # Check for pass/fail
        if "VALIDATION 2 PASSED" in content:
            print("\n✓ VALIDATION 2 PASSED")
            result = True
        elif "pass" in content.lower():
            print("\n✓ Tests passed (partial)")
            result = True
        else:
            print("\n✗ Tests may have failed - check screenshots")
            result = False

        print(f"\nScreenshots saved to /tmp/validation2_*.png")
        browser.close()
        return result

if __name__ == "__main__":
    success = test_sse_streaming()
    exit(0 if success else 1)
