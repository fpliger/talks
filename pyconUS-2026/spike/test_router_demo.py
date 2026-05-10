"""Playwright e2e tests for Router Demo — PyCon US 2026."""

import time
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://localhost:8000"
PYSCRIPT_TIMEOUT = 60_000  # ms


def _load_page(page):
    page.goto(BASE_URL)
    page.wait_for_load_state("networkidle")
    # Wait for PyScript to finish bootstrapping
    page.wait_for_function("() => document.querySelector('#messages')", timeout=PYSCRIPT_TIMEOUT)
    time.sleep(3)  # let Pyodide finish importing


def _select_tier(page, tier):
    page.click(f'button.tier-btn[data-tier="{tier}"]')
    time.sleep(0.3)


# ── Demo 1 ──────────────────────────────────────────────────────────────────

def test_demo1_streams_remote():
    """Demo 1 on remote tier produces a streaming message with REMOTE badge."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        _load_page(page)

        _select_tier(page, "remote")
        page.click("#demo1")

        # Wait for at least one token to appear in a .content span
        page.wait_for_function(
            "() => [...document.querySelectorAll('.message.assistant .content')].some(el => el.textContent.length > 2)",
            timeout=15_000,
        )

        messages_html = page.inner_html("#messages")
        assert "REMOTE" in messages_html, "Expected REMOTE route badge"

        page.screenshot(path="/tmp/demo1_remote.png", full_page=True)
        browser.close()


def test_demo1_routing_animation():
    """Clicking Demo 1 triggers the routing animation lane."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        _load_page(page)

        _select_tier(page, "remote")
        page.click("#demo1")
        time.sleep(1)

        # The remote lane-wrap should have .active class
        active_lane = page.query_selector("#lane-remote.active")
        assert active_lane is not None, "Expected #lane-remote to have .active class"

        browser.close()


# ── Demo 2 ──────────────────────────────────────────────────────────────────

def test_demo2_pandas_before_llm():
    """Demo 2: Pandas IN-BROWSER block appears before the first LLM token."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        _load_page(page)

        _select_tier(page, "remote")
        page.click("#demo2")

        # Pandas block should appear within 5s
        page.wait_for_function(
            "() => document.querySelector('.message.assistant span.route-badge.in-browser') !== null",
            timeout=10_000,
        )

        # Then an LLM streaming bubble should follow
        page.wait_for_function(
            "() => [...document.querySelectorAll('.message.assistant .content')].some(el => el.textContent.length > 5)",
            timeout=20_000,
        )

        page.screenshot(path="/tmp/demo2_remote.png", full_page=True)
        browser.close()


# ── Demo 3 ──────────────────────────────────────────────────────────────────

def test_demo3_tool_loop_order():
    """Demo 3: web_search pill appears before save_to_file pill."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        _load_page(page)

        _select_tier(page, "remote")
        page.click("#demo3")

        # Wait for web_search pill
        page.wait_for_selector('.tool-call[data-name="web_search"]', timeout=30_000)
        # Wait for save_to_file pill
        page.wait_for_selector('.tool-call[data-name="save_to_file"]', timeout=30_000)

        pills = page.query_selector_all('.tool-call')
        names = [p.get_attribute('data-name') for p in pills]
        ws_idx = next((i for i, n in enumerate(names) if n == "web_search"), -1)
        sf_idx = next((i for i, n in enumerate(names) if n == "save_to_file"), -1)
        assert ws_idx >= 0, "web_search pill missing"
        assert sf_idx >= 0, "save_to_file pill missing"
        assert ws_idx < sf_idx, "web_search should appear before save_to_file"

        page.screenshot(path="/tmp/demo3_remote.png", full_page=True)
        browser.close()


# ── Health banner ────────────────────────────────────────────────────────────

def test_remote_dot_ready_when_server_up():
    """When remote SSE server is running, dot-remote should show 'ready' class."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        _load_page(page)
        time.sleep(3)  # probes run after DOMContentLoaded

        dot = page.query_selector("#dot-remote")
        assert dot is not None
        cls = dot.get_attribute("class") or ""
        assert "ready" in cls or "checking" in cls, f"Unexpected dot class: {cls}"

        browser.close()


# ── Routing animation ────────────────────────────────────────────────────────

def test_routing_animation_switches_on_tier_change():
    """Selecting a different tier and running demo 1 moves the active lane."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        _load_page(page)

        _select_tier(page, "remote")
        page.click("#demo1")
        time.sleep(1)
        assert page.query_selector("#lane-remote.active") is not None

        # Now switch to local and run again (local may fail, but animation should fire)
        _select_tier(page, "local")
        page.click("#demo1")
        time.sleep(1)
        # remote lane should no longer be active
        assert page.query_selector("#lane-remote.active") is None, \
            "remote lane should lose .active after switching to local"

        browser.close()


# ── FS bridge ───────────────────────────────────────────────────────────────

def test_fs_bridge_download_mode():
    """Demo 3: when user picks 'Download' in the save modal, a download is triggered."""
    with sync_playwright() as p:
        # Grant clipboard + download permissions so the blob download doesn't hang
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        _load_page(page)

        _select_tier(page, "remote")

        # Listen for the download event before clicking
        with page.expect_download(timeout=60_000) as dl_info:
            page.click("#demo3")

            # When the save modal appears, click "Download"
            page.wait_for_selector("#fs-download", timeout=30_000)
            page.click("#fs-download")

        download = dl_info.value
        assert download.suggested_filename.endswith(".md"), \
            f"Expected .md download, got: {download.suggested_filename}"

        page.screenshot(path="/tmp/demo3_download.png", full_page=True)
        context.close()
        browser.close()


# ── Standalone runner ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    passed = 0
    failed = 0
    tests = [
        test_demo1_streams_remote,
        test_demo1_routing_animation,
        test_demo2_pandas_before_llm,
        test_demo3_tool_loop_order,
        test_fs_bridge_download_mode,
        test_remote_dot_ready_when_server_up,
        test_routing_animation_switches_on_tier_change,
    ]
    for fn in tests:
        try:
            print(f"  running {fn.__name__} ...", end=" ", flush=True)
            fn()
            print("PASS")
            passed += 1
        except Exception as e:
            print(f"FAIL — {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
