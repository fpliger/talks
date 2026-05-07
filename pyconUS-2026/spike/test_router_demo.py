"""Playwright test for Router Demo."""

from playwright.sync_api import sync_playwright
import time

def test_router_demo():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console
        def log_console(msg):
            print(f"  CONSOLE: [{msg.type}] {msg.text[:100]}")
        page.on("console", log_console)

        print("Loading router demo...")
        page.goto("http://localhost:8000")
        page.wait_for_load_state("networkidle")

        try:
            page.wait_for_selector("text=Router demo loaded", timeout=60000)
            print("PyScript loaded!")
        except:
            print("Waiting for PyScript...")
            time.sleep(5)

        page.screenshot(path="/tmp/router_initial.png", full_page=True)

        # Test Demo 1: Local Only
        print("\n--- Demo 1: Local Only ---")
        page.click("#demo1")
        time.sleep(2)
        page.screenshot(path="/tmp/router_demo1.png", full_page=True)

        # Test Demo 2: Hybrid
        print("\n--- Demo 2: Hybrid ---")
        page.click("#demo2")
        time.sleep(4)  # Needs streaming time
        page.screenshot(path="/tmp/router_demo2.png", full_page=True)

        # Test Demo 3: Remote + Tools
        print("\n--- Demo 3: Remote + Tools ---")
        page.click("#demo3")
        time.sleep(8)  # More complex - needs time for full agent loop
        page.screenshot(path="/tmp/router_demo3.png", full_page=True)

        # Get final state
        messages = page.inner_html("#messages")
        print("\n--- Messages Content ---")
        print(messages[:1500])

        # Check results
        has_local = "LOCAL" in messages
        has_hybrid = "HYBRID" in messages
        has_remote = "REMOTE" in messages
        has_tool = "TOOL" in messages

        print(f"\nRoute badges found: local={has_local}, hybrid={has_hybrid}, remote={has_remote}, tool={has_tool}")

        if has_local and has_hybrid and has_remote:
            print("\n✓ ROUTER DEMO WORKING - All 3 paths demonstrated")
            result = True
        else:
            print("\n⚠ Some paths may not have triggered correctly")
            result = False

        print("\nScreenshots saved to /tmp/router_*.png")
        browser.close()
        return result

if __name__ == "__main__":
    success = test_router_demo()
    exit(0 if success else 1)
