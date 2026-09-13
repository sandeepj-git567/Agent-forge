"""
Evaluation Datasets and Metrics Models for AgentForge AI
"""
from pydantic import BaseModel, Field


class EvalTestCase(BaseModel):
    """Single test case entry in evaluation dataset."""
    id: str
    input: str
    expected_output: str
    criteria: list[str] = Field(default_factory=lambda: ["groundedness", "relevance", "correctness"])


class EvaluationResult(BaseModel):
    """Results from evaluating an agent run against evaluation criteria."""
    eval_id: str
    run_id: str
    correctness_score: float = Field(..., ge=0.0, le=1.0)
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    groundedness_score: float = Field(..., ge=0.0, le=1.0)
    citation_quality_score: float = Field(..., ge=0.0, le=1.0)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    feedback: str


BENCHMARK_DATASET: list[EvalTestCase] = [
    EvalTestCase(
        id="bench-001",
        input="Research enterprise AI agent frameworks",
        expected_output="Detailed overview of Google ADK 2.9.0 multi-agent architecture and RAG",
        criteria=["groundedness", "relevance", "citation_quality"]
    ),
    EvalTestCase(
        id="bench-002",
        input="Write a python function to add two numbers safely",
        expected_output="def add(a: float, b: float) -> float: return a + b",
        criteria=["correctness", "relevance"]
    )
]
