"""Measure cold start and bundle sizes for the router demo."""

from playwright.sync_api import sync_playwright
import time

def measure_cold_start():
    """Measure time from navigation to PyScript ready."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Clear cache for true cold start
        page.context.clear_cookies()

        print("Measuring cold start (first load, no cache)...")
        start_time = time.time()

        page.goto("http://localhost:8000")

        # Wait for PyScript to be fully loaded
        try:
            page.wait_for_selector("text=Router demo loaded", timeout=120000)
            ready_time = time.time()
            cold_start = ready_time - start_time
            print(f"Cold start (PyScript ready): {cold_start:.2f}s")
        except:
            print("PyScript did not load within timeout")
            cold_start = None

        # Measure subsequent load (warm)
        print("\nMeasuring warm start (cached)...")
        start_time = time.time()
        page.reload()
        try:
            page.wait_for_selector("text=Router demo loaded", timeout=60000)
            warm_time = time.time() - start_time
            print(f"Warm start (cached): {warm_time:.2f}s")
        except:
            warm_time = None

        browser.close()
        return cold_start, warm_time


def measure_network():
    """Measure network transfer sizes."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Track all responses
        responses = []
        def handle_response(response):
            try:
                size = len(response.body()) if response.ok else 0
            except:
                size = 0
            responses.append({
                'url': response.url,
                'size': size,
                'status': response.status
            })

        page.on('response', handle_response)

        page.goto("http://localhost:8000")
        page.wait_for_load_state("networkidle")

        # Wait a bit more for PyScript
        time.sleep(5)

        # Analyze
        total_size = sum(r['size'] for r in responses)
        pyscript_size = sum(r['size'] for r in responses if 'pyscript' in r['url'].lower())
        pyodide_size = sum(r['size'] for r in responses if 'pyodide' in r['url'].lower())

        print(f"\nNetwork transfer analysis:")
        print(f"Total transferred: {total_size / 1024 / 1024:.2f} MB")
        print(f"PyScript core: {pyscript_size / 1024:.0f} KB")

        # Show largest resources
        sorted_responses = sorted(responses, key=lambda x: x['size'], reverse=True)[:10]
        print("\nTop 10 resources by size:")
        for r in sorted_responses:
            url_short = r['url'].split('/')[-1][:50]
            print(f"  {r['size']/1024:.0f} KB - {url_short}")

        browser.close()
        return total_size, pyscript_size


if __name__ == "__main__":
    print("=" * 60)
    print("Router Demo Metrics")
    print("=" * 60)

    cold, warm = measure_cold_start()
    total, pyscript = measure_network()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Cold start: {cold:.2f}s" if cold else "Cold start: FAILED")
    print(f"Warm start: {warm:.2f}s" if warm else "Warm start: FAILED")
    print(f"Total bundle: {total/1024/1024:.2f} MB" if total else "Bundle: UNKNOWN")
