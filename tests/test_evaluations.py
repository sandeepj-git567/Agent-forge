"""
Comprehensive Unit Tests for AI Evaluation Engine & Metrics (Stage 8)
"""
import pytest
from fastapi.testclient import TestClient

from agentforge.api.main import app
from agentforge.eval.evaluator import default_evaluator
from agentforge.eval.metrics import (
    calculate_citation_quality,
    calculate_correctness,
    calculate_groundedness,
    calculate_relevance,
    calculate_retrieval_precision_recall,
)

client = TestClient(app)


def test_metrics_calculations():
    # 1. Relevance
    rel = calculate_relevance("Research AI agents", "This report covers multi-agent orchestration and AI agents.")
    assert 0.0 <= rel <= 1.0
    assert rel > 0.5

    # 2. Groundedness
    grd = calculate_groundedness("Based on retrieved evidence, the plan is validated.", context_snippets=["evidence 1"])
    assert 0.0 <= grd <= 1.0
    assert grd > 0.6

    # 3. Correctness
    corr = calculate_correctness("def add(a, b): return a + b", "def add(a: float, b: float) -> float: return a + b")
    assert 0.0 <= corr <= 1.0
    assert corr > 0.4

    # 4. Citation Quality
    cite = calculate_citation_quality("Source: https://docs.agentforge.ai [1]", sources=[{"id": "s1"}])
    assert cite >= 0.8

    # 5. Precision & Recall
    pr = calculate_retrieval_precision_recall(["d1", "d2", "d3"], ["d1", "d2", "d4"])
    assert pr["precision"] == 0.67
    assert pr["recall"] == 0.67
    assert pr["f1"] == 0.67


def test_evaluator_response_scoring():
    res = default_evaluator.evaluate_response(
        input_text="What is AgentForge AI?",
        actual_output="AgentForge AI is an enterprise multi-agent platform using Google ADK 2.9.0. Source: https://agentforge.ai",
        expected_output="Enterprise multi-agent framework based on Google ADK"
    )
    assert res.overall_score >= 0.65
    assert res.correctness_score > 0.0
    assert res.relevance_score > 0.0
    assert res.groundedness_score > 0.0
    assert res.citation_quality_score > 0.0


def test_evaluations_api_endpoints():
    # 1. Single evaluation run
    eval_payload = {
        "input_text": "Write a python sorting function",
        "actual_output": "def sort_list(lst): return sorted(lst)",
        "expected_output": "def sort_list(lst: list) -> list: return sorted(lst)"
    }
    run_res = client.post("/api/v1/evaluations/run", json=eval_payload)
    assert run_res.status_code == 201
    data = run_res.json()
    assert "eval_id" in data
    assert "overall_score" in data

    # 2. Get list of evaluations from DB
    list_res = client.get("/api/v1/evaluations")
    assert list_res.status_code == 200
    assert len(list_res.json()) > 0

    # 3. Get benchmark test cases list
    bench_res = client.get("/api/v1/evaluations/benchmarks")
    assert bench_res.status_code == 200
    assert bench_res.json()["count"] >= 5


@pytest.mark.asyncio
async def test_batch_benchmark_execution():
    bench_run_res = client.post("/api/v1/evaluations/benchmark/run")
    assert bench_run_res.status_code == 200
    data = bench_run_res.json()
    assert "benchmark_id" in data
    assert data["total_cases"] >= 5
    assert data["avg_overall_score"] > 0.0
    assert len(data["results"]) == data["total_cases"]
