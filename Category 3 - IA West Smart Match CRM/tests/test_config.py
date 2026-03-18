"""Tests for configuration validation behavior."""

from pathlib import Path

import src.config as config


def _write_required_csvs(data_dir: Path) -> None:
    """Create the required CSV placeholders for config validation tests."""
    for file_name in [
        config.SPEAKER_PROFILES_CSV,
        config.CPP_EVENTS_CSV,
        config.CPP_COURSES_CSV,
        config.EVENT_CALENDAR_CSV,
    ]:
        (data_dir / file_name).write_text("header\nvalue\n", encoding="utf-8")


def test_validate_config_allows_app_boot_without_openai_key(tmp_path: Path, monkeypatch) -> None:
    """Sprint 0 app boot should only require local data files."""
    _write_required_csvs(tmp_path)
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "OPENAI_API_KEY", "")

    assert config.validate_config() == []


def test_validate_config_requires_openai_key_for_embedding_flows(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Embedding flows should still enforce a real OpenAI API key."""
    _write_required_csvs(tmp_path)
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    monkeypatch.setattr(config, "OPENAI_API_KEY", "sk-...")

    errors = config.validate_config(require_openai=True)

    assert "OPENAI_API_KEY is not set or is still the placeholder value" in errors
