"""
Automated AI Agent Evaluation Engine for AgentForge AI
"""
import uuid
from typing import Any

from agentforge.eval.datasets import EvaluationResult
from agentforge.eval.metrics import (
    calculate_citation_quality,
    calculate_correctness,
    calculate_groundedness,
    calculate_relevance,
)


class AIEvaluator:
    """Evaluates agent responses for correctness, relevance, groundedness, and citation quality."""

    @staticmethod
    def evaluate_response(
        input_text: str,
        actual_output: str,
        expected_output: str = "",
        context_snippets: list[str] | None = None,
        sources: list[dict[str, Any]] | None = None
    ) -> EvaluationResult:
        """Calculate evaluation scores using deterministic metrics engine."""
        relevance = calculate_relevance(input_text, actual_output)
        groundedness = calculate_groundedness(actual_output, context_snippets)
        correctness = calculate_correctness(actual_output, expected_output)
        citation_quality = calculate_citation_quality(actual_output, sources)

        overall = round((correctness * 0.3) + (relevance * 0.3) + (groundedness * 0.2) + (citation_quality * 0.2), 2)

        feedback = (
            f"Evaluation result: Overall score {overall:.2f} (Correctness: {correctness:.2f}, "
            f"Relevance: {relevance:.2f}, Groundedness: {groundedness:.2f}, Citation Quality: {citation_quality:.2f})."
        )

        return EvaluationResult(
            eval_id=f"eval-{uuid.uuid4().hex[:8]}",
            run_id=f"run-{uuid.uuid4().hex[:8]}",
            correctness_score=correctness,
            relevance_score=relevance,
            groundedness_score=groundedness,
            citation_quality_score=citation_quality,
            overall_score=overall,
            feedback=feedback
        )


default_evaluator = AIEvaluator()
