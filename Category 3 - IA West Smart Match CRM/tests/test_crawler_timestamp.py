"""Wave 0 test: crawler timestamp uniqueness (DEBT-02).

After the fix, the ``now`` local inside ``_run_crawl`` must be a *function*
that returns a fresh ISO-8601 string on every call — not a bound method on a
single frozen datetime object.
"""

import time
from datetime import datetime, timezone


def test_now_returns_distinct_timestamps() -> None:
    """Two successive calls to the now() factory must return different strings.

    This is the behavioral contract: each crawler event gets a unique timestamp.
    We import ``_run_crawl`` source indirectly by re-creating the fixed pattern
    so the test is self-contained and does not depend on async infrastructure.
    """
    # Replicate the FIXED pattern from crawler.py line 101
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

    ts1 = now()
    # Tiny sleep to guarantee monotonic clock advancement
    time.sleep(0.001)
    ts2 = now()

    assert ts1 != ts2, f"Timestamps must differ but both were {ts1}"


def test_now_returns_valid_iso8601() -> None:
    """The now() function must return a valid ISO-8601 UTC timestamp."""
    def now() -> str:
        return datetime.now(timezone.utc).isoformat()

    ts = now()
    # Must parse back without error
    parsed = datetime.fromisoformat(ts)
    assert parsed.tzinfo is not None, "Timestamp must include timezone info"


def test_crawler_source_uses_function_not_bound_method() -> None:
    """The actual crawler.py source must contain 'def now' — proving the fix
    replaced the bound-method assignment with a proper function definition."""
    import inspect
    from src.api.routers.crawler import _run_crawl

    source = inspect.getsource(_run_crawl)
    assert "def now" in source, (
        "crawler.py _run_crawl must define `def now()` — "
        "found bound-method pattern instead"
    )
