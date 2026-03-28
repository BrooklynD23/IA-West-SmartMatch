"""
Standalone runner for React E2E Playwright tests.

Usage:
    python scripts/run_react_e2e.py

Requires React at :5173 and FastAPI at :8000 to be running.
Start both: python start_fullstack.py

The runner imports test functions from tests/test_react_e2e.py, executes them
sequentially, prints a pass/fail summary, and exits non-zero if any test fails.

Screenshots are written to output/playwright/ relative to the project root
(same directory as the QA runner scripts).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add project root to sys.path so the tests module is importable.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.test_react_e2e import test_feedback_flow, test_qr_flow  # noqa: E402


def main() -> None:
    results: list[dict[str, str]] = []

    for name, fn in [
        ("qr_flow", test_qr_flow),
        ("feedback_flow", test_feedback_flow),
    ]:
        print(f"\n{'=' * 60}")
        print(f"Running: {name}")
        print(f"{'=' * 60}")
        start = time.time()
        try:
            fn()
            elapsed = time.time() - start
            print(f"PASS: {name} ({elapsed:.1f}s)")
            results.append({"name": name, "status": "pass", "time": f"{elapsed:.1f}s"})
        except Exception as exc:
            elapsed = time.time() - start
            print(f"FAIL: {name} ({elapsed:.1f}s) -- {exc}")
            results.append(
                {
                    "name": name,
                    "status": "fail",
                    "time": f"{elapsed:.1f}s",
                    "error": str(exc),
                }
            )

    print(f"\n{'=' * 60}")
    print("Summary")
    print(f"{'=' * 60}")
    for r in results:
        status_marker = "PASS" if r["status"] == "pass" else "FAIL"
        print(f"  [{status_marker}] {r['name']} ({r['time']})")

    failed = [r for r in results if r["status"] != "pass"]
    if failed:
        print(f"\n{len(failed)} test(s) failed.")
        sys.exit(1)
    else:
        print("\nAll tests passed.")


if __name__ == "__main__":
    main()
