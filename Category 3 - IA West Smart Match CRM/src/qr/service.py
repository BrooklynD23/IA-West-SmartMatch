"""Deterministic QR generation, scan logging, and ROI statistics."""

from __future__ import annotations

import base64
import hashlib
import json
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import qrcode

from src.ui.data_helpers import (
    _data_dir,
    _load_qr_manifest_cached,
    _load_qr_scan_log_cached,
    load_qr_manifest,
    load_qr_scan_log,
)

DEFAULT_DESTINATION_URL = "https://www.insightsassociation.org/"
DEFAULT_BASE_URL = "http://127.0.0.1:8000"
TRUSTED_DESTINATION_HOSTS = ("insightsassociation.org", "www.insightsassociation.org")
QR_DIRNAME = "qr"
MANIFEST_FILENAME = "manifest.json"
SCAN_LOG_FILENAME = "scan-log.jsonl"


def _qr_dir() -> Path:
    return _data_dir() / QR_DIRNAME


def _manifest_path() -> Path:
    return _qr_dir() / MANIFEST_FILENAME


def _scan_log_path() -> Path:
    return _qr_dir() / SCAN_LOG_FILENAME


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _normalize(value: str) -> str:
    return " ".join(value.split()).casefold()


def deterministic_referral_code(speaker_name: str, event_name: str) -> str:
    """Return a stable referral code for a speaker/event pair."""
    payload = f"{_normalize(speaker_name)}|{_normalize(event_name)}"
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    token = base64.b32encode(digest).decode("ascii").rstrip("=").upper()[:12]
    return f"IAW-{token}"


def _build_scan_url(base_url: str, referral_code: str) -> str:
    return f"{base_url.rstrip('/')}/api/qr/scan/{referral_code}"


def _normalize_host(value: str) -> str:
    host = value.strip().casefold()
    if ":" in host:
        return host.split(":", 1)[0]
    return host


def _parse_absolute_url(value: str, *, label: str) -> Any:
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError(f"{label} must be an absolute http(s) URL")
    if parts.username or parts.password:
        raise ValueError(f"{label} must not include user credentials")
    return parts


def _host_matches(candidate_host: str, allowed_host: str) -> bool:
    return candidate_host == allowed_host or candidate_host.endswith(f".{allowed_host}")


def _normalize_base_url(base_url: str) -> str:
    parts = _parse_absolute_url(base_url, label="base_url")
    return urlunsplit((parts.scheme, parts.netloc, "", "", ""))


def _allowed_destination_hosts(base_url: str, scan_url: str | None = None) -> set[str]:
    hosts = {_normalize_host(host) for host in TRUSTED_DESTINATION_HOSTS}
    hosts.add(_normalize_host(urlsplit(_normalize_base_url(base_url)).netloc))
    if scan_url:
        hosts.add(_normalize_host(urlsplit(scan_url).netloc))
    return {host for host in hosts if host}


def _normalize_destination_url(destination_url: str, *, base_url: str, scan_url: str | None = None) -> str:
    parts = _parse_absolute_url(destination_url, label="destination_url")
    host = _normalize_host(parts.netloc)
    allowed_hosts = _allowed_destination_hosts(base_url, scan_url=scan_url)
    if not any(_host_matches(host, allowed_host) for allowed_host in allowed_hosts):
        raise ValueError("destination_url must stay on the app host or an approved Insights Association domain")
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, parts.fragment))


def _append_query_params(url: str, params: dict[str, Any]) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    for key, value in params.items():
        if value is None:
            continue
        query[key] = str(value)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _render_qr_png(scan_url: str) -> bytes:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=4,
    )
    qr.add_data(scan_url)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#005394", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _read_manifest_records() -> list[dict[str, Any]]:
    return [dict(record) for record in load_qr_manifest()]


def _write_manifest_records(records: list[dict[str, Any]]) -> None:
    qr_dir = _qr_dir()
    qr_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "updated_at": _utc_now(),
        "record_count": len(records),
        "records": records,
    }
    _manifest_path().write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    _load_qr_manifest_cached.cache_clear()


def _append_scan_log(entry: dict[str, Any]) -> None:
    qr_dir = _qr_dir()
    qr_dir.mkdir(parents=True, exist_ok=True)
    with _scan_log_path().open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=True))
        fh.write("\n")
    _load_qr_scan_log_cached.cache_clear()


def _merge_manifest_record(
    records: list[dict[str, Any]],
    referral_code: str,
    speaker_name: str,
    event_name: str,
    destination_url: str,
    scan_url: str,
) -> dict[str, Any]:
    now = _utc_now()
    for record in records:
        if record.get("referral_code") == referral_code:
            record.update(
                {
                    "speaker_name": speaker_name,
                    "event_name": event_name,
                    "destination_url": destination_url,
                    "scan_url": scan_url,
                    "updated_at": now,
                    "generation_count": int(record.get("generation_count", 0) or 0) + 1,
                }
            )
            record.setdefault("scan_count", int(record.get("scan_count", 0) or 0))
            record.setdefault(
                "membership_interest_count",
                int(record.get("membership_interest_count", 0) or 0),
            )
            record.setdefault("last_scanned_at", record.get("last_scanned_at", ""))
            return record

    record = {
        "referral_code": referral_code,
        "speaker_name": speaker_name,
        "event_name": event_name,
        "destination_url": destination_url,
        "scan_url": scan_url,
        "generated_at": now,
        "updated_at": now,
        "generation_count": 1,
        "scan_count": 0,
        "membership_interest_count": 0,
        "last_scanned_at": "",
    }
    records.append(record)
    return record


def generate_qr_artifact(
    speaker_name: str,
    event_name: str,
    destination_url: str | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    """Create or refresh a deterministic QR asset for one speaker/event pair."""
    referral_code = deterministic_referral_code(speaker_name, event_name)
    records = _read_manifest_records()
    normalized_base_url = _normalize_base_url(base_url or DEFAULT_BASE_URL)
    scan_url = _build_scan_url(normalized_base_url, referral_code)
    normalized_destination_url = _normalize_destination_url(
        destination_url or DEFAULT_DESTINATION_URL,
        base_url=normalized_base_url,
        scan_url=scan_url,
    )
    manifest_record = _merge_manifest_record(
        records,
        referral_code=referral_code,
        speaker_name=speaker_name,
        event_name=event_name,
        destination_url=normalized_destination_url,
        scan_url=scan_url,
    )
    _write_manifest_records(records)

    png_bytes = _render_qr_png(scan_url)
    qr_png_base64 = base64.b64encode(png_bytes).decode("ascii")

    return {
        **manifest_record,
        "qr_png_base64": qr_png_base64,
        "qr_data_url": f"data:image/png;base64,{qr_png_base64}",
    }


def _find_manifest_record(referral_code: str) -> dict[str, Any] | None:
    for record in load_qr_manifest():
        if str(record.get("referral_code", "")) == referral_code:
            return dict(record)
    return None


def record_qr_scan(
    referral_code: str,
    membership_interest: bool = False,
    destination_url: str | None = None,
) -> dict[str, Any]:
    """Append a scan event and return the redirect target metadata."""
    record = _find_manifest_record(referral_code)
    if record is None:
        raise KeyError(f"Unknown referral code: {referral_code}")

    now = _utc_now()
    base_url = str(record.get("scan_url", "") or DEFAULT_BASE_URL)
    redirect_target = _normalize_destination_url(
        destination_url or str(record.get("destination_url", "") or DEFAULT_DESTINATION_URL),
        base_url=base_url,
        scan_url=base_url,
    )
    redirect_url = _append_query_params(
        redirect_target,
        {
            "referral_code": referral_code,
            "speaker_name": record.get("speaker_name", ""),
            "event_name": record.get("event_name", ""),
            "membership_interest": str(bool(membership_interest)).lower(),
        },
    )

    scan_entry = {
        "referral_code": referral_code,
        "speaker_name": record.get("speaker_name", ""),
        "event_name": record.get("event_name", ""),
        "destination_url": redirect_target,
        "redirect_url": redirect_url,
        "scanned_at": now,
        "membership_interest": bool(membership_interest),
    }
    _append_scan_log(scan_entry)

    records = _read_manifest_records()
    for manifest_record in records:
        if manifest_record.get("referral_code") == referral_code:
            manifest_record["scan_count"] = int(manifest_record.get("scan_count", 0) or 0) + 1
            manifest_record["last_scanned_at"] = now
            if membership_interest:
                manifest_record["membership_interest_count"] = (
                    int(manifest_record.get("membership_interest_count", 0) or 0) + 1
                )
            manifest_record["updated_at"] = now
            manifest_record["destination_url"] = redirect_target
            break
    _write_manifest_records(records)
    _load_qr_manifest_cached.cache_clear()

    return {
        "redirect_url": redirect_url,
        "scan_entry": scan_entry,
        "manifest_record": _find_manifest_record(referral_code),
    }


def build_qr_stats(
    speaker_name: str | None = None,
    event_name: str | None = None,
    referral_code: str | None = None,
) -> dict[str, Any]:
    """Return aggregate QR generation, scan, and ROI stats."""
    manifest_records = load_qr_manifest()
    scan_records = load_qr_scan_log()

    def _matches(record: dict[str, Any]) -> bool:
        if speaker_name and _normalize(str(record.get("speaker_name", ""))) != _normalize(speaker_name):
            return False
        if event_name and _normalize(str(record.get("event_name", ""))) != _normalize(event_name):
            return False
        if referral_code and str(record.get("referral_code", "")) != referral_code:
            return False
        return True

    filtered_manifest = [dict(record) for record in manifest_records if _matches(record)]
    filtered_scans = [dict(record) for record in scan_records if _matches(record)]

    scan_count = len(filtered_scans)
    membership_interest_count = sum(1 for record in filtered_scans if bool(record.get("membership_interest")))
    conversion_rate = round(membership_interest_count / scan_count, 4) if scan_count else 0.0

    per_referral: list[dict[str, Any]] = []
    scan_counts: dict[str, int] = {}
    interest_counts: dict[str, int] = {}
    for scan in filtered_scans:
        code = str(scan.get("referral_code", ""))
        scan_counts[code] = scan_counts.get(code, 0) + 1
        if bool(scan.get("membership_interest")):
            interest_counts[code] = interest_counts.get(code, 0) + 1

    for record in filtered_manifest:
        code = str(record.get("referral_code", ""))
        scans = scan_counts.get(code, int(record.get("scan_count", 0) or 0))
        interests = interest_counts.get(code, int(record.get("membership_interest_count", 0) or 0))
        per_referral.append(
            {
                "referral_code": code,
                "speaker_name": record.get("speaker_name", ""),
                "event_name": record.get("event_name", ""),
                "generation_count": int(record.get("generation_count", 0) or 0),
                "scan_count": scans,
                "membership_interest_count": interests,
                "conversion_rate": round(interests / scans, 4) if scans else 0.0,
                "scan_url": record.get("scan_url", ""),
                "destination_url": record.get("destination_url", ""),
                "generated_at": record.get("generated_at", ""),
                "last_scanned_at": record.get("last_scanned_at", ""),
            }
        )

    per_referral.sort(key=lambda item: (-item["scan_count"], item["referral_code"]))
    recent_scans = sorted(filtered_scans, key=lambda item: str(item.get("scanned_at", "")), reverse=True)[:10]

    return {
        "generated_count": len(filtered_manifest),
        "scan_count": scan_count,
        "membership_interest_count": membership_interest_count,
        "conversion_rate": conversion_rate,
        "unique_speakers": len({str(record.get("speaker_name", "")) for record in filtered_manifest}),
        "unique_events": len({str(record.get("event_name", "")) for record in filtered_manifest}),
        "referral_codes": per_referral,
        "recent_scans": recent_scans,
        "filters": {
            "speaker_name": speaker_name,
            "event_name": event_name,
            "referral_code": referral_code,
        },
    }
