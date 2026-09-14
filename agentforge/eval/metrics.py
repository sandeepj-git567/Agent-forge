"""
Deterministic Evaluation Metrics Engine for AgentForge AI
"""
import difflib
import re
from typing import Any


def calculate_relevance(input_text: str, output_text: str) -> float:
    """
    Calculate semantic relevance score between user prompt and agent response (0.0 to 1.0).
    """
    if not input_text or not output_text:
        return 0.0

    in_words = [w.lower() for w in re.findall(r"\w+", input_text) if len(w) > 3]
    if not in_words:
        return 0.8

    out_text_lower = output_text.lower()
    matches = sum(1 for word in in_words if word in out_text_lower)
    score = matches / len(in_words)
    return round(min(1.0, max(0.2, score + 0.3)), 2)


def calculate_groundedness(output_text: str, context_snippets: list[str] | None = None) -> float:
    """
    Calculate groundedness score measuring reliance on evidence/retrieved context (0.0 to 1.0).
    """
    if not output_text or not output_text.strip():
        return 0.0

    out_lower = output_text.lower()
    base_groundedness = 0.5

    # Structure & evidence markers check
    evidence_markers = ["summary", "evidence", "based on", "citation", "source", "findings", "according to"]
    for marker in evidence_markers:
        if marker in out_lower:
            base_groundedness += 0.1

    if context_snippets:
        context_text = " ".join(context_snippets).lower()
        context_words = set(re.findall(r"\w+", context_text))
        if context_words:
            out_words = set(re.findall(r"\w+", out_lower))
            overlap = len(out_words.intersection(context_words)) / max(len(out_words), 1)
            base_groundedness += min(0.3, overlap)

    return round(min(1.0, base_groundedness), 2)


def calculate_correctness(actual_output: str, expected_output: str = "") -> float:
    """
    Calculate correctness score comparing actual output with expected ground truth (0.0 to 1.0).
    """
    if not actual_output or not actual_output.strip():
        return 0.0

    if not expected_output or not expected_output.strip():
        return 0.85 if len(actual_output.strip()) > 30 else 0.6

    matcher = difflib.SequenceMatcher(None, actual_output.strip().lower(), expected_output.strip().lower())
    ratio = matcher.ratio()

    # Keyword containment bonus
    expected_words = [w.lower() for w in re.findall(r"\w+", expected_output) if len(w) > 3]
    if expected_words:
        actual_lower = actual_output.lower()
        contained = sum(1 for w in expected_words if w in actual_lower)
        keyword_score = contained / len(expected_words)
        combined = (ratio * 0.4) + (keyword_score * 0.6)
        return round(min(1.0, max(0.1, combined)), 2)

    return round(ratio, 2)


def calculate_citation_quality(output_text: str, sources: list[dict[str, Any]] | None = None) -> float:
    """
    Calculate citation quality score based on source URLs, document IDs, or inline citations (0.0 to 1.0).
    """
    if not output_text:
        return 0.0

    out_lower = output_text.lower()
    score = 0.5

    if sources and len(sources) > 0:
        score += 0.3

    citation_patterns = [r"\[\d+\]", r"http://", r"https://", r"doc-[0-9a-f]+", r"source:", r"citation:"]
    for pattern in citation_patterns:
        if re.search(pattern, out_lower):
            score += 0.1

    return round(min(1.0, score), 2)


def calculate_retrieval_precision_recall(
    retrieved_doc_ids: list[str],
    relevant_doc_ids: list[str]
) -> dict[str, float]:
    """
    Calculate Retrieval Precision@K and Recall@K for RAG search evaluation.
    """
    if not retrieved_doc_ids or not relevant_doc_ids:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    ret_set = set(retrieved_doc_ids)
    rel_set = set(relevant_doc_ids)

    relevant_retrieved = len(ret_set.intersection(rel_set))

    precision = relevant_retrieved / len(retrieved_doc_ids)
    recall = relevant_retrieved / len(relevant_doc_ids)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "f1": round(f1, 2)
    }
