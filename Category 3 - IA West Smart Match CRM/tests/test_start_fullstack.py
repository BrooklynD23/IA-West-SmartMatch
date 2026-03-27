"""Focused tests for the CAT3 fullstack launcher helpers."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def load_start_fullstack_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "start_fullstack.py"
    spec = importlib.util.spec_from_file_location("cat3_start_fullstack", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


start_fullstack = load_start_fullstack_module()


def test_build_frontend_command_uses_strict_port() -> None:
    command = start_fullstack.build_frontend_command("npm", "127.0.0.1", 5173)

    assert "--strictPort" in command


def test_startup_failure_detail_prefers_log_tail(tmp_path: Path) -> None:
    log_path = tmp_path / "frontend.log"
    log_path.write_text("first line\nlast useful line\n", encoding="utf-8")

    detail = start_fullstack.startup_failure_detail("Process exited with code 1", log_path)

    assert detail == "last useful line"


def test_log_contains_phrase_detects_address_in_use(tmp_path: Path) -> None:
    log_path = tmp_path / "backend.log"
    log_path.write_text("ERROR: [Errno 98] Address already in use\n", encoding="utf-8")

    assert start_fullstack.log_contains_phrase(log_path, "Address already in use") is True


def test_resolve_backend_port_conflict_reuses_running_backend(monkeypatch) -> None:
    monkeypatch.setattr(start_fullstack, "service_ready", lambda url, timeout_seconds: True)

    reused, detail = start_fullstack.resolve_backend_port_conflict(
        "http://127.0.0.1:8000/api/health",
        "127.0.0.1",
        8000,
        None,
    )

    assert reused is True
    assert detail == "Already running | http://127.0.0.1:8000/api/health"


def test_resolve_backend_port_conflict_reports_explicit_port_error(tmp_path: Path, monkeypatch) -> None:
    log_path = tmp_path / "backend.log"
    log_path.write_text("ERROR: [Errno 98] Address already in use\n", encoding="utf-8")
    monkeypatch.setattr(start_fullstack, "service_ready", lambda url, timeout_seconds: False)

    reused, detail = start_fullstack.resolve_backend_port_conflict(
        "http://127.0.0.1:8000/api/health",
        "127.0.0.1",
        8000,
        log_path,
    )

    assert reused is False
    assert detail == f"Port 127.0.0.1:8000 already in use | {log_path}"
