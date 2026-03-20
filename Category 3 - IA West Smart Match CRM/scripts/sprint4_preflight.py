#!/usr/bin/env python3
"""Sprint 4 preflight and optional cache prewarm utility."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import CACHE_DIR, DATA_DIR, GEMINI_API_KEY, PROJECT_ROOT
from src.embeddings import EMBEDDING_CACHE_FILES
from src.extraction.llm_extractor import extract_events
from src.scraping.scraper import UNIVERSITY_TARGETS, scrape_university

DEMO_FIXTURES_DIR = CACHE_DIR / "demo_fixtures"
SCRAPE_CACHE_DIR = CACHE_DIR / "scrapes"
EXTRACTION_CACHE_DIR = CACHE_DIR / "extractions"
EXPLANATION_CACHE_DIR = CACHE_DIR / "explanations"
EMAIL_CACHE_DIR = CACHE_DIR / "emails"
EXPECTED_RUNTIME = "python-3.11"

DEMO_FIXTURE_FILES = [
    "discovery_scan.json",
    "email_generation.json",
    "expansion_connections.json",
    "feedback_summary.json",
    "match_explanations.json",
    "pipeline_funnel.json",
    "volunteer_metrics.json",
]

DATA_FILES = [
    "data_speaker_profiles.csv",
    "data_cpp_events_contacts.csv",
    "data_cpp_course_schedule.csv",
    "data_event_calendar.csv",
]

ROOT_FILES = [
    "requirements.txt",
    ".streamlit/config.toml",
]


@dataclass
class CheckResult:
    name: str
    status: str
    details: str


def _ok(name: str, details: str) -> CheckResult:
    return CheckResult(name=name, status="ok", details=details)


def _warn(name: str, details: str) -> CheckResult:
    return CheckResult(name=name, status="warn", details=details)


def _fail(name: str, details: str) -> CheckResult:
    return CheckResult(name=name, status="fail", details=details)


def check_data_files() -> list[CheckResult]:
    results: list[CheckResult] = []
    for file_name in DATA_FILES:
        path = DATA_DIR / file_name
        if path.exists():
            results.append(_ok(file_name, f"Found {path}"))
        else:
            results.append(_fail(file_name, f"Missing required data file: {path}"))
    return results


def check_root_files() -> list[CheckResult]:
    results: list[CheckResult] = []
    for relative_path in ROOT_FILES:
        path = PROJECT_ROOT / relative_path
        if path.exists():
            results.append(_ok(relative_path, f"Found {path}"))
        else:
            results.append(_fail(relative_path, f"Missing required deployment file: {path}"))
    return results


def check_runtime_file() -> CheckResult:
    path = PROJECT_ROOT / "runtime.txt"
    if not path.exists():
        return _fail("runtime.txt", f"Missing required deployment file: {path}")

    runtime_value = path.read_text(encoding="utf-8").strip()
    if runtime_value != EXPECTED_RUNTIME:
        return _fail(
            "runtime.txt",
            f"Expected {EXPECTED_RUNTIME} for Streamlit Cloud, found {runtime_value or '[empty]'}.",
        )
    return _ok("runtime.txt", f"Found {path} with expected runtime {runtime_value}.")


def check_demo_fixtures() -> list[CheckResult]:
    results: list[CheckResult] = []
    for file_name in DEMO_FIXTURE_FILES:
        path = DEMO_FIXTURES_DIR / file_name
        if path.exists():
            results.append(_ok(file_name, f"Found {path}"))
        else:
            results.append(_fail(file_name, f"Missing demo fixture: {path}"))
    return results


def check_embedding_cache() -> CheckResult:
    missing = [
        file_name
        for file_name in EMBEDDING_CACHE_FILES
        if not (CACHE_DIR / file_name).exists()
    ]
    manifest = CACHE_DIR / "cache_manifest.json"
    if missing or not manifest.exists():
        missing_items = [*missing]
        if not manifest.exists():
            missing_items.append("cache_manifest.json")
        return _warn(
            "embedding_cache",
            "Missing embedding artifacts: " + ", ".join(missing_items),
        )
    return _ok("embedding_cache", "Embedding cache artifacts are present.")


def check_cache_dir(path: Path, name: str) -> CheckResult:
    if not path.exists():
        return _warn(name, f"{path} does not exist yet.")
    count = len([file for file in path.iterdir() if file.is_file()])
    if count == 0:
        return _warn(name, f"{path} exists but contains no files.")
    return _ok(name, f"{path} contains {count} file(s).")


def prewarm_discovery() -> list[CheckResult]:
    results: list[CheckResult] = []
    if not GEMINI_API_KEY:
        return [_warn("prewarm_discovery", "Skipped: GEMINI_API_KEY is not configured.")]

    for university, cfg in UNIVERSITY_TARGETS.items():
        try:
            scrape_result = scrape_university(
                url=cfg["url"],
                method=cfg["method"],  # type: ignore[arg-type]
            )
            events = extract_events(
                raw_html=str(scrape_result.get("html", "")),
                university=university,
                url=cfg["url"],
                prefer_cache=True,
            )
            results.append(
                _ok(
                    f"prewarm:{university}",
                    f"{scrape_result.get('source', 'unknown')} -> {len(events)} extracted event(s)",
                )
            )
        except Exception as exc:
            results.append(_warn(f"prewarm:{university}", str(exc)))
    return results


def render_text_report(results: list[CheckResult]) -> str:
    lines = ["Sprint 4 Preflight", ""]
    for result in results:
        lines.append(f"[{result.status.upper()}] {result.name}: {result.details}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path to write the full preflight report as JSON.",
    )
    parser.add_argument(
        "--prewarm-discovery",
        action="store_true",
        help="Warm scrape and extraction caches for all configured universities.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero on warnings as well as failures.",
    )
    args = parser.parse_args()

    results: list[CheckResult] = []
    results.extend(check_data_files())
    results.extend(check_root_files())
    results.append(check_runtime_file())
    results.extend(check_demo_fixtures())
    results.append(check_embedding_cache())
    results.append(check_cache_dir(SCRAPE_CACHE_DIR, "scrape_cache"))
    results.append(check_cache_dir(EXTRACTION_CACHE_DIR, "extraction_cache"))
    results.append(check_cache_dir(EXPLANATION_CACHE_DIR, "explanation_cache"))
    results.append(check_cache_dir(EMAIL_CACHE_DIR, "email_cache"))

    if args.prewarm_discovery:
        results.extend(prewarm_discovery())

    report = [asdict(result) for result in results]
    print(render_text_report(results))

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    has_fail = any(result.status == "fail" for result in results)
    has_warn = any(result.status == "warn" for result in results)
    if has_fail or (args.strict and has_warn):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
