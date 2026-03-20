"""Tests for Sprint 4 preflight utility behavior."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_preflight_module() -> ModuleType:
    script_path = Path(__file__).resolve().parent.parent / "scripts" / "sprint4_preflight.py"
    spec = importlib.util.spec_from_file_location("sprint4_preflight_test", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_prewarm_discovery_uses_cache_persistence_flag(monkeypatch) -> None:
    module = _load_preflight_module()
    calls: list[dict] = []

    monkeypatch.setattr(module, "GEMINI_API_KEY", "AIza-test")
    monkeypatch.setattr(
        module,
        "UNIVERSITY_TARGETS",
        {"UCLA": {"url": "https://career.ucla.edu/events/", "method": "bs4"}},
    )
    monkeypatch.setattr(
        module,
        "scrape_university",
        lambda url, method: {"html": "<html>ok</html>", "source": "live"},
    )

    def fake_extract_events(**kwargs):
        calls.append(kwargs)
        return [{"event_name": "Cached Event"}]

    monkeypatch.setattr(module, "extract_events", fake_extract_events)

    results = module.prewarm_discovery()

    assert len(results) == 1
    assert results[0].status == "ok"
    assert calls[0]["prefer_cache"] is True


def test_check_runtime_file_requires_expected_streamlit_runtime(tmp_path: Path, monkeypatch) -> None:
    module = _load_preflight_module()

    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    (tmp_path / "runtime.txt").write_text("3.12.3\n", encoding="utf-8")

    result = module.check_runtime_file()

    assert result.status == "fail"
    assert "python-3.11" in result.details
