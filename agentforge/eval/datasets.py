"""
Evaluation Datasets and Metrics Models for AgentForge AI
"""
from typing import Any
from pydantic import BaseModel, Field


class EvalTestCase(BaseModel):
    """Single test case entry in evaluation dataset."""
    id: str = Field(..., description="Unique test case ID")
    input: str = Field(..., description="User prompt or task input")
    expected_output: str = Field(..., description="Target ground truth response")
    mode: str = Field(default="general", description="Task mode (general, coding, research, rag)")
    criteria: list[str] = Field(default_factory=lambda: ["correctness", "relevance", "groundedness", "citation_quality"])


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


class BenchmarkRunSummary(BaseModel):
    """Summary of batch benchmark execution across all test cases."""
    benchmark_id: str
    total_cases: int
    passed_cases: int
    avg_correctness: float
    avg_relevance: float
    avg_groundedness: float
    avg_citation_quality: float
    avg_overall_score: float
    results: list[dict[str, Any]]


BENCHMARK_DATASET: list[EvalTestCase] = [
    EvalTestCase(
        id="bench-001",
        input="Research enterprise AI agent frameworks",
        expected_output="Detailed overview of Google ADK 2.9.0 multi-agent architecture and RAG",
        mode="research",
        criteria=["groundedness", "relevance", "citation_quality"]
    ),
    EvalTestCase(
        id="bench-002",
        input="Write a python function to add two numbers safely",
        expected_output="def add(a: float, b: float) -> float: return a + b",
        mode="coding",
        criteria=["correctness", "relevance"]
    ),
    EvalTestCase(
        id="bench-003",
        input="What framework does AgentForge AI use for agent orchestration?",
        expected_output="AgentForge AI uses Google ADK 2.9.0 for primary agent orchestration.",
        mode="rag",
        criteria=["groundedness", "correctness", "citation_quality"]
    ),
    EvalTestCase(
        id="bench-004",
        input="Design a DAG workflow for data processing",
        expected_output="Topological DAG graph with nodes: plan, extract, transform, load, review.",
        mode="general",
        criteria=["correctness", "relevance"]
    ),
    EvalTestCase(
        id="bench-005",
        input="Perform security audit on Python code",
        expected_output="AST inspection identifying dangerous eval exec system calls and unsafe imports.",
        mode="coding",
        criteria=["correctness", "groundedness"]
    )
]
