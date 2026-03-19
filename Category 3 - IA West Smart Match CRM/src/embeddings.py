"""Gemini embedding generation with caching and retry logic."""

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import numpy as np
from src.config import (
    CACHE_DIR,
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_DIMENSION,
    EMBEDDING_MAX_RETRIES,
    GEMINI_API_KEY,
    GEMINI_EMBEDDING_MODEL,
    has_gemini_api_key,
)
from src.gemini_client import GeminiAPIError, batch_embed_texts
from src.utils import format_course_identifier, normalize_course_section

logger = logging.getLogger(__name__)

SPEAKER_EMBEDDINGS_FILE = "speaker_embeddings.npy"
SPEAKER_METADATA_FILE = "speaker_metadata.json"
EVENT_EMBEDDINGS_FILE = "event_embeddings.npy"
EVENT_METADATA_FILE = "event_metadata.json"
COURSE_EMBEDDINGS_FILE = "course_embeddings.npy"
COURSE_METADATA_FILE = "course_metadata.json"
EMBEDDING_CACHE_FILES = (
    SPEAKER_EMBEDDINGS_FILE,
    SPEAKER_METADATA_FILE,
    EVENT_EMBEDDINGS_FILE,
    EVENT_METADATA_FILE,
    COURSE_EMBEDDINGS_FILE,
    COURSE_METADATA_FILE,
)


def _get_api_key() -> str:
    """Return a validated Gemini API key."""
    if not has_gemini_api_key():
        raise ValueError("GEMINI_API_KEY is not set or is still the placeholder value")
    return GEMINI_API_KEY


def _retry_with_backoff(
    func,
    max_retries: int = EMBEDDING_MAX_RETRIES,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
):
    """
    Execute func() with exponential backoff on retryable errors.

    Retries on GeminiAPIError when the failure is retryable.
    """
    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            return func()
        except GeminiAPIError as e:
            last_exception = e
            if e.retryable and attempt < max_retries:
                delay = min(base_delay * (2**attempt), max_delay)
                logger.warning("Gemini API error. Retry %d/%d in %.1fs", attempt + 1, max_retries, delay)
                time.sleep(delay)
            else:
                raise
    raise last_exception


def compose_speaker_text(row: dict) -> str:
    """
    Compose the embedding input text for a speaker profile.

    Concatenates: expertise_tags + title + company + board_role.
    """
    parts = [
        str(row.get("Expertise Tags", "") or ""),
        str(row.get("Title", "") or ""),
        str(row.get("Company", "") or ""),
        str(row.get("Board Role", "") or ""),
    ]
    text = " ".join(part for part in parts if part.strip())
    if len(text) > 500:
        logger.warning("Speaker text exceeds 500 chars (%d): %s...", len(text), text[:50])
    return text


def compose_event_text(row: dict) -> str:
    """
    Compose the embedding input text for a CPP event.

    Concatenates: event_name + category + volunteer_roles + primary_audience.
    """
    parts = [
        str(row.get("Event / Program", "") or ""),
        str(row.get("Category", "") or ""),
        str(row.get("Volunteer Roles (fit)", "") or ""),
        str(row.get("Primary Audience", "") or ""),
    ]
    return " ".join(part for part in parts if part.strip())


def compose_course_text(row: dict) -> str:
    """
    Compose the embedding input text for a CPP course section.

    Concatenates: title + guest_lecture_fit.
    """
    fit = str(row.get("Guest Lecture Fit", "") or "")
    if not fit.strip():
        fit = "Medium"
        logger.warning("Course '%s' has empty Guest Lecture Fit — defaulting to 'Medium'", row.get("Title", "unknown"))
    parts = [
        str(row.get("Title", "") or ""),
        fit,
    ]
    return " ".join(part for part in parts if part.strip())


def generate_embeddings(
    texts: list[str],
    model: Optional[str] = None,
    batch_size: Optional[int] = None,
) -> np.ndarray:
    """
    Generate embeddings for a list of texts using the Gemini API.

    Returns:
        numpy array of shape (len(texts), EMBEDDING_DIMENSION).
    """
    if model is None:
        model = GEMINI_EMBEDDING_MODEL
    if batch_size is None:
        batch_size = EMBEDDING_BATCH_SIZE

    if not texts:
        return np.empty((0, EMBEDDING_DIMENSION), dtype=np.float32)

    for i, text in enumerate(texts):
        if not text.strip():
            raise ValueError(f"Text at index {i} is empty after stripping")

    api_key = _get_api_key()
    all_embeddings = []

    for batch_start in range(0, len(texts), batch_size):
        batch_texts = texts[batch_start : batch_start + batch_size]

        def _call_api(batch=batch_texts):
            return batch_embed_texts(
                batch,
                api_key=api_key,
                model=model,
                output_dimensionality=EMBEDDING_DIMENSION,
                batch_size=len(batch),
            )

        batch_embeddings = _retry_with_backoff(_call_api)
        all_embeddings.extend(batch_embeddings)

    embeddings_array = np.array(all_embeddings, dtype=np.float32)

    if embeddings_array.shape != (len(texts), EMBEDDING_DIMENSION):
        raise ValueError(
            f"Expected shape ({len(texts)}, {EMBEDDING_DIMENSION}), got {embeddings_array.shape}"
        )

    return embeddings_array


def _load_manifest(manifest_path: Path) -> dict:
    """Load a cache manifest if present, otherwise return an empty manifest."""
    if not manifest_path.exists():
        return {}
    with open(manifest_path) as f:
        return json.load(f)


def _load_metadata(meta_path: Path) -> list[dict]:
    """Load JSON metadata for an embedding cache."""
    with open(meta_path, encoding="utf-8") as f:
        metadata = json.load(f)

    if not isinstance(metadata, list):
        raise ValueError(f"Metadata at {meta_path} must be a list")
    if any(not isinstance(entry, dict) for entry in metadata):
        raise ValueError(f"Metadata at {meta_path} must contain dict entries only")

    return metadata


def _save_metadata(meta_path: Path, metadata: list[dict]) -> None:
    """Persist embedding metadata as JSON to avoid unsafe deserialization."""
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def _text_hash(texts: list[str]) -> str:
    """Return a stable hash for the embedding input payload."""
    payload = json.dumps(texts, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_cached_embeddings(
    emb_path: Path,
    meta_path: Path,
    manifest_path: Path,
    manifest_key: str,
    texts: list[str],
) -> Optional[tuple[np.ndarray, list[dict]]]:
    """Return cached embeddings when the manifest still matches the current payload."""
    if not (emb_path.exists() and meta_path.exists() and manifest_path.exists()):
        return None

    try:
        manifest = _load_manifest(manifest_path)
        entry = manifest.get(manifest_key, {})
        expected_shape = (len(texts), EMBEDDING_DIMENSION)
        expected_hash = _text_hash(texts)

        if entry.get("row_count") != len(texts):
            return None
        if entry.get("model") != GEMINI_EMBEDDING_MODEL:
            return None
        if entry.get("dimension") != EMBEDDING_DIMENSION:
            return None
        if entry.get("text_hash") != expected_hash:
            return None

        embeddings = np.load(emb_path)
        metadata = _load_metadata(meta_path)

        if embeddings.shape != expected_shape:
            logger.warning("Ignoring cache with unexpected shape at %s: %s", emb_path, embeddings.shape)
            return None
        if len(metadata) != len(texts):
            logger.warning("Ignoring cache with unexpected metadata length at %s", meta_path)
            return None
        return embeddings, metadata
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        logger.warning("Ignoring unreadable cache artifacts for %s: %s", manifest_key, exc)
        return None


def _build_lookup_dict(
    embeddings: np.ndarray,
    metadata: list[dict],
    key_name: str,
    label: str,
) -> dict[str, np.ndarray]:
    """Build a stable key->embedding mapping from cached metadata."""
    if len(metadata) != len(embeddings):
        raise ValueError(
            f"{label.title()} metadata length {len(metadata)} does not match embedding rows {len(embeddings)}"
        )

    lookup: dict[str, np.ndarray] = {}
    for index, meta in enumerate(metadata):
        key = meta.get(key_name)
        if not key:
            raise ValueError(f"Missing '{key_name}' in {label} metadata row {index}")
        lookup[str(key)] = embeddings[index]
    return lookup


def _build_course_lookup_dict(
    embeddings: np.ndarray,
    metadata: list[dict],
) -> dict[str, np.ndarray]:
    """Build course lookup keys from cached course metadata."""
    if len(metadata) != len(embeddings):
        raise ValueError(
            f"Course metadata length {len(metadata)} does not match embedding rows {len(embeddings)}"
        )

    lookup: dict[str, np.ndarray] = {}
    for index, meta in enumerate(metadata):
        key = format_course_identifier(
            meta.get("course"),
            meta.get("section"),
        )
        if not key:
            raise ValueError(f"Missing course identifier data in course metadata row {index}")
        lookup[key] = embeddings[index]
    return lookup


def _load_lookup_dict(
    emb_path: Path,
    meta_path: Path,
    label: str,
    key_name: str | None = None,
) -> dict[str, np.ndarray]:
    """Load an embedding lookup dict from cache, returning an empty mapping on failure."""
    if not (emb_path.exists() and meta_path.exists()):
        return {}

    try:
        embeddings = np.load(emb_path)
        metadata = _load_metadata(meta_path)
        if key_name is None:
            lookup = _build_course_lookup_dict(embeddings, metadata)
        else:
            lookup = _build_lookup_dict(embeddings, metadata, key_name=key_name, label=label)
        logger.info("Loaded %d %s embeddings.", len(lookup), label)
        return lookup
    except (json.JSONDecodeError, OSError, ValueError):
        logger.exception("Failed to load %s embeddings from cache.", label)
        return {}


def load_embedding_lookup_dicts(
    cache_dir: Optional[Path] = None,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Load speaker, event, and course embedding lookup dicts from disk."""
    cache_dir = cache_dir or CACHE_DIR
    speaker_lookup = _load_lookup_dict(
        cache_dir / SPEAKER_EMBEDDINGS_FILE,
        cache_dir / SPEAKER_METADATA_FILE,
        label="speaker",
        key_name="name",
    )
    event_lookup = _load_lookup_dict(
        cache_dir / EVENT_EMBEDDINGS_FILE,
        cache_dir / EVENT_METADATA_FILE,
        label="event",
        key_name="event_name",
    )
    course_lookup = _load_lookup_dict(
        cache_dir / COURSE_EMBEDDINGS_FILE,
        cache_dir / COURSE_METADATA_FILE,
        label="course",
    )
    return speaker_lookup, event_lookup, course_lookup


def generate_embedding_lookup_dicts(
    speakers_df,
    events_df,
    courses_df,
    cache_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Generate or reuse cache artifacts, then return lookup dicts for matching."""
    cache_dir = cache_dir or CACHE_DIR
    speaker_embeddings, speaker_metadata = embed_speakers(
        speakers_df,
        cache_dir=cache_dir,
        force_refresh=force_refresh,
    )
    event_embeddings, event_metadata = embed_events(
        events_df,
        cache_dir=cache_dir,
        force_refresh=force_refresh,
    )
    course_embeddings, course_metadata = embed_courses(
        courses_df,
        cache_dir=cache_dir,
        force_refresh=force_refresh,
    )
    return (
        _build_lookup_dict(speaker_embeddings, speaker_metadata, key_name="name", label="speaker"),
        _build_lookup_dict(event_embeddings, event_metadata, key_name="event_name", label="event"),
        _build_course_lookup_dict(course_embeddings, course_metadata),
    )


def _update_manifest(manifest_path: Path, key: str, row_count: int, text_hash: str) -> None:
    """Update the cache manifest JSON with a new entry."""
    manifest = _load_manifest(manifest_path)
    manifest[key] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "row_count": row_count,
        "model": GEMINI_EMBEDDING_MODEL,
        "dimension": EMBEDDING_DIMENSION,
        "text_hash": text_hash,
    }
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)


def embed_speakers(
    speakers_df,
    cache_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> tuple[np.ndarray, list[dict]]:
    """
    Generate and cache embeddings for all speaker profiles.

    Cache files: speaker_embeddings.npy, speaker_metadata.json, cache_manifest.json
    """
    cache_dir = cache_dir or CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)

    emb_path = cache_dir / SPEAKER_EMBEDDINGS_FILE
    meta_path = cache_dir / SPEAKER_METADATA_FILE
    manifest_path = cache_dir / "cache_manifest.json"

    texts = []
    metadata = []
    for _, row in speakers_df.iterrows():
        text = compose_speaker_text(row.to_dict())
        texts.append(text)
        metadata.append({
            "name": row["Name"],
            "board_role": row["Board Role"],
            "metro_region": row["Metro Region"],
            "company": row.get("Company", ""),
            "title": row.get("Title", ""),
            "expertise_tags": row["Expertise Tags"],
            "embedding_text": text,
        })

    if not force_refresh:
        cached = _load_cached_embeddings(
            emb_path=emb_path,
            meta_path=meta_path,
            manifest_path=manifest_path,
            manifest_key="speaker_embeddings",
            texts=texts,
        )
        if cached is not None:
            return cached

    embeddings = generate_embeddings(texts)

    np.save(emb_path, embeddings)
    _save_metadata(meta_path, metadata)

    _update_manifest(
        manifest_path,
        "speaker_embeddings",
        len(speakers_df),
        _text_hash(texts),
    )

    return embeddings, metadata


def embed_events(
    events_df,
    cache_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> tuple[np.ndarray, list[dict]]:
    """
    Generate and cache embeddings for all CPP events.

    Cache files: event_embeddings.npy, event_metadata.json, cache_manifest.json
    """
    cache_dir = cache_dir or CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)

    emb_path = cache_dir / EVENT_EMBEDDINGS_FILE
    meta_path = cache_dir / EVENT_METADATA_FILE
    manifest_path = cache_dir / "cache_manifest.json"

    texts = []
    metadata = []
    for _, row in events_df.iterrows():
        text = compose_event_text(row.to_dict())
        texts.append(text)
        metadata.append({
            "event_name": row["Event / Program"],
            "category": row["Category"],
            "volunteer_roles": row.get("Volunteer Roles (fit)", ""),
            "primary_audience": row.get("Primary Audience", ""),
            "host_unit": row.get("Host / Unit", ""),
            "url": row.get("Public URL", ""),
            "embedding_text": text,
        })

    if not force_refresh:
        cached = _load_cached_embeddings(
            emb_path=emb_path,
            meta_path=meta_path,
            manifest_path=manifest_path,
            manifest_key="event_embeddings",
            texts=texts,
        )
        if cached is not None:
            return cached

    embeddings = generate_embeddings(texts)

    np.save(emb_path, embeddings)
    _save_metadata(meta_path, metadata)

    _update_manifest(
        manifest_path,
        "event_embeddings",
        len(events_df),
        _text_hash(texts),
    )

    return embeddings, metadata


def embed_courses(
    courses_df,
    cache_dir: Optional[Path] = None,
    force_refresh: bool = False,
) -> tuple[np.ndarray, list[dict]]:
    """
    Generate and cache embeddings for all CPP course sections.

    Cache files: course_embeddings.npy, course_metadata.json, cache_manifest.json
    """
    cache_dir = cache_dir or CACHE_DIR
    cache_dir.mkdir(parents=True, exist_ok=True)

    emb_path = cache_dir / COURSE_EMBEDDINGS_FILE
    meta_path = cache_dir / COURSE_METADATA_FILE
    manifest_path = cache_dir / "cache_manifest.json"

    texts = []
    metadata = []
    for _, row in courses_df.iterrows():
        text = compose_course_text(row.to_dict())
        texts.append(text)
        metadata.append({
            "instructor": row["Instructor"],
            "course": row["Course"],
            "section": normalize_course_section(row.get("Section")),
            "title": row["Title"],
            "days": row["Days"],
            "start_time": row.get("Start Time", ""),
            "end_time": row.get("End Time", ""),
            "enrl_cap": int(row.get("Enrl Cap", 0)),
            "mode": row["Mode"],
            "guest_lecture_fit": row["Guest Lecture Fit"],
            "embedding_text": text,
        })

    if not force_refresh:
        cached = _load_cached_embeddings(
            emb_path=emb_path,
            meta_path=meta_path,
            manifest_path=manifest_path,
            manifest_key="course_embeddings",
            texts=texts,
        )
        if cached is not None:
            return cached

    embeddings = generate_embeddings(texts)

    np.save(emb_path, embeddings)
    _save_metadata(meta_path, metadata)

    _update_manifest(
        manifest_path,
        "course_embeddings",
        len(courses_df),
        _text_hash(texts),
    )

    return embeddings, metadata
