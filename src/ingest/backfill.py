"""Backfill publisher with a rate limit (issue #3)."""
import time

MAX_MSGS_PER_SEC = 5000  # broker throttles above this; measured in the 1-month test


def publish_all(readings, send):
    window_start, sent = time.monotonic(), 0
    for r in readings:
        if sent >= MAX_MSGS_PER_SEC:
            elapsed = time.monotonic() - window_start
            if elapsed < 1:
                time.sleep(1 - elapsed)
            window_start, sent = time.monotonic(), 0
        send(r)
        sent += 1
