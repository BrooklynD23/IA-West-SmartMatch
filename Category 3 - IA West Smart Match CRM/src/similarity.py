"""Cosine similarity computation and validation for IA SmartMatch."""

import numpy as np


def cosine_similarity_matrix(
    embeddings_a: np.ndarray,
    embeddings_b: np.ndarray,
) -> np.ndarray:
    """
    Compute pairwise cosine similarity between two sets of embeddings.

    Args:
        embeddings_a: Array of shape (m, d) — e.g., speaker embeddings.
        embeddings_b: Array of shape (n, d) — e.g., event embeddings.

    Returns:
        Similarity matrix of shape (m, n) with values in [-1, 1].
        Entry [i, j] = cosine_similarity(a[i], b[j]).

    Raises:
        ValueError: If embedding dimensions don't match.
    """
    if embeddings_a.shape[1] != embeddings_b.shape[1]:
        raise ValueError(
            f"Embedding dimensions don't match: "
            f"{embeddings_a.shape[1]} vs {embeddings_b.shape[1]}"
        )

    norms_a = np.linalg.norm(embeddings_a, axis=1, keepdims=True)
    norms_b = np.linalg.norm(embeddings_b, axis=1, keepdims=True)

    norms_a = np.maximum(norms_a, 1e-10)
    norms_b = np.maximum(norms_b, 1e-10)

    normalized_a = embeddings_a / norms_a
    normalized_b = embeddings_b / norms_b

    return normalized_a @ normalized_b.T


def cosine_similarity_pair(
    embedding_a: np.ndarray,
    embedding_b: np.ndarray,
) -> float:
    """
    Compute cosine similarity between two individual embeddings.

    Args:
        embedding_a: 1D array of shape (d,).
        embedding_b: 1D array of shape (d,).

    Returns:
        Scalar cosine similarity in [-1, 1].
    """
    dot_product = np.dot(embedding_a, embedding_b)
    norm_a = np.linalg.norm(embedding_a)
    norm_b = np.linalg.norm(embedding_b)

    if norm_a < 1e-10 or norm_b < 1e-10:
        return 0.0

    return float(dot_product / (norm_a * norm_b))


def get_top_k_matches(
    similarity_matrix: np.ndarray,
    source_metadata: list[dict],
    target_metadata: list[dict],
    k: int = 3,
) -> list[dict]:
    """
    For each target (event/course), return the top-k most similar sources (speakers).

    Args:
        similarity_matrix: Shape (n_speakers, n_events), from cosine_similarity_matrix.
        source_metadata: List of speaker metadata dicts (length = n_speakers).
        target_metadata: List of event/course metadata dicts (length = n_events).
        k: Number of top matches to return per target.

    Returns:
        List of dicts, one per target, each containing:
            - target: target metadata dict
            - matches: list of k dicts, each with source, score, rank
    """
    n_sources, n_targets = similarity_matrix.shape
    k = min(k, n_sources)
    results = []

    for target_idx in range(n_targets):
        scores = similarity_matrix[:, target_idx]
        top_indices = np.argsort(scores)[::-1][:k]

        matches = []
        for rank, source_idx in enumerate(top_indices, start=1):
            matches.append({
                "source": source_metadata[source_idx],
                "score": float(scores[source_idx]),
                "rank": rank,
            })

        results.append({
            "target": target_metadata[target_idx],
            "matches": matches,
        })

    return results


def validate_similarity_scores(
    similarity_matrix: np.ndarray,
    source_metadata: list[dict],
    target_metadata: list[dict],
    min_spread: float = 0.15,
) -> dict:
    """
    Validate that embeddings produce meaningfully different match scores.

    This is the Sprint 0 Go/No-Go gate check.

    Args:
        similarity_matrix: Shape (n_speakers, n_events).
        source_metadata: Speaker metadata.
        target_metadata: Event/course metadata.
        min_spread: Minimum required spread between top and bottom match.

    Returns:
        Dict with passed, overall_max, overall_min, overall_spread,
        per_target_spreads, targets_passing, targets_total, message.
    """
    n_sources, n_targets = similarity_matrix.shape
    overall_max = float(np.max(similarity_matrix))
    overall_min = float(np.min(similarity_matrix))
    overall_spread = overall_max - overall_min

    per_target = []
    targets_passing = 0

    for target_idx in range(n_targets):
        col = similarity_matrix[:, target_idx]
        col_max = float(np.max(col))
        col_min = float(np.min(col))
        spread = col_max - col_min

        target_name = target_metadata[target_idx].get(
            "event_name",
            target_metadata[target_idx].get("title", f"target_{target_idx}"),
        )

        per_target.append({
            "target_name": target_name,
            "max_score": col_max,
            "min_score": col_min,
            "spread": spread,
            "passes": spread >= min_spread,
        })

        if spread >= min_spread:
            targets_passing += 1

    passed = overall_spread >= min_spread and targets_passing >= n_targets * 0.5

    if passed:
        message = (
            f"PASS: Overall spread {overall_spread:.4f} >= {min_spread}. "
            f"{targets_passing}/{n_targets} targets have sufficient spread. "
            f"Embeddings produce meaningfully different match scores."
        )
    else:
        message = (
            f"FAIL: Overall spread {overall_spread:.4f}, "
            f"only {targets_passing}/{n_targets} targets have spread >= {min_spread}. "
            f"Consider pivoting to TF-IDF + keyword overlap."
        )

    return {
        "passed": passed,
        "overall_max": overall_max,
        "overall_min": overall_min,
        "overall_spread": overall_spread,
        "per_target_spreads": per_target,
        "targets_passing": targets_passing,
        "targets_total": n_targets,
        "message": message,
    }


def keyword_overlap_score(
    speaker_tags: str,
    event_text: str,
) -> float:
    """
    Compute simple keyword overlap score between speaker tags and event text.

    Used as a baseline comparison against embedding-based similarity.

    Args:
        speaker_tags: Comma-separated expertise tags string.
        event_text: Event description text (name + category + roles + audience).

    Returns:
        Jaccard-like overlap score in [0, 1].
    """
    speaker_words = set(
        word.strip().lower()
        for word in speaker_tags.replace(",", " ").split()
        if len(word.strip()) > 2
    )
    event_words = set(
        word.strip().lower()
        for word in event_text.replace(",", " ").replace(";", " ").split()
        if len(word.strip()) > 2
    )

    if not speaker_words or not event_words:
        return 0.0

    intersection = speaker_words & event_words
    union = speaker_words | event_words

    return len(intersection) / len(union)
