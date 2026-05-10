"""In-page metrics helpers.

Records time-to-first-token (TTFT) for each demo run and pushes it to
the JS metrics strip via window.recordTtft().
"""

import time
from pyscript import window


def start_timer() -> float:
    return time.monotonic()


def record_ttft(start: float):
    """Call this when the first token arrives. Pushes ms to the JS strip."""
    ms = int((time.monotonic() - start) * 1000)
    try:
        window.recordTtft(ms)
    except Exception:
        pass
