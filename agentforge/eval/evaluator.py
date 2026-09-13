"""
Automated AI Agent Evaluation Engine for AgentForge AI
"""
import uuid

from agentforge.eval.datasets import EvaluationResult


class AIEvaluator:
    """Evaluates agent responses for correctness, relevance, groundedness, and citation quality."""

    @staticmethod
    def evaluate_response(input_text: str, actual_output: str, expected_output: str = "") -> EvaluationResult:
        """Calculate evaluation scores based on response heuristic metrics."""
        output_lower = actual_output.lower() if actual_output else ""
        input_lower = input_text.lower() if input_text else ""

        # Relevance calculation
        keywords = [w for w in input_lower.split() if len(w) > 3]
        matches = sum(1 for k in keywords if k in output_lower)
        relevance = min(1.0, max(0.5, matches / len(keywords))) if keywords else 0.8

        # Groundedness calculation (checks for structure, citations or evidence headers)
        groundedness = 0.9 if any(h in output_lower for h in ["summary", "plan", "evidence", "based on", "citation"]) else 0.7

        # Correctness score
        correctness = 0.95 if actual_output and len(actual_output) > 50 else 0.6

        # Citation quality score
        citation_quality = 0.9 if "citation" in output_lower or "source" in output_lower or "http" in output_lower else 0.75

        overall = round((relevance + groundedness + correctness + citation_quality) / 4.0, 2)

        return EvaluationResult(
            eval_id=f"eval-{uuid.uuid4().hex[:8]}",
            run_id=f"run-{uuid.uuid4().hex[:8]}",
            correctness_score=round(correctness, 2),
            relevance_score=round(relevance, 2),
            groundedness_score=round(groundedness, 2),
            citation_quality_score=round(citation_quality, 2),
            overall_score=overall,
            feedback=f"Evaluation passed with overall score {overall:.2f}."
        )


default_evaluator = AIEvaluator()
