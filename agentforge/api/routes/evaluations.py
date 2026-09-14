"""
Database-Backed AI Agent Evaluation API Router
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from agentforge.db.models import Evaluation
from agentforge.db.session import get_db
from agentforge.eval.datasets import BENCHMARK_DATASET, BenchmarkRunSummary
from agentforge.eval.evaluator import default_evaluator
from agentforge.runtime.executor import agent_runtime_executor

router = APIRouter(prefix="/evaluations", tags=["AI Agent Evaluation Engine"])


class EvaluationRequest(BaseModel):
    """Payload for POST /api/v1/evaluations/run"""
    input_text: str = Field(..., description="Original user prompt input")
    actual_output: str = Field(..., description="Actual agent output to evaluate")
    expected_output: str = Field(default="", description="Expected ground truth criteria")
    context_snippets: list[str] | None = Field(default=None, description="Optional RAG context snippets")


@router.post("/run", status_code=status.HTTP_201_CREATED)
async def run_evaluation(payload: EvaluationRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Execute automated evaluation metrics on agent output and persist to database."""
    res = default_evaluator.evaluate_response(
        input_text=payload.input_text,
        actual_output=payload.actual_output,
        expected_output=payload.expected_output,
        context_snippets=payload.context_snippets
    )
    result_dict = res.model_dump()

    # Persist in DB
    db_eval = Evaluation(
        id=res.eval_id,
        run_id=res.run_id,
        groundedness_score=res.groundedness_score,
        relevance_score=res.relevance_score,
        citation_score=res.citation_quality_score,
        feedback=res.feedback,
        metrics={
            "correctness_score": res.correctness_score,
            "overall_score": res.overall_score
        }
    )
    db.add(db_eval)
    db.commit()

    return result_dict


@router.post("/benchmark/run", response_model=dict[str, Any])
async def run_benchmark_evaluations(db: Session = Depends(get_db)) -> dict[str, Any]:
    """
    Run batch automated evaluation benchmark across pre-packaged dataset test cases.
    Executes agent for each test case, computes scores, and returns aggregated summary.
    """
    benchmark_id = f"bench-run-{uuid.uuid4().hex[:8]}"
    eval_results: list[dict[str, Any]] = []

    total_correctness = 0.0
    total_relevance = 0.0
    total_groundedness = 0.0
    total_citation = 0.0
    total_overall = 0.0
    passed_cases = 0

    for test_case in BENCHMARK_DATASET:
        # Execute agent task for test case
        exec_res = await agent_runtime_executor.run_task(task=test_case.input, mode=test_case.mode)
        actual_output = exec_res.get("answer") or ""

        res = default_evaluator.evaluate_response(
            input_text=test_case.input,
            actual_output=actual_output,
            expected_output=test_case.expected_output
        )

        case_res = {
            "case_id": test_case.id,
            "input": test_case.input,
            "actual_output": actual_output[:200] + "..." if len(actual_output) > 200 else actual_output,
            "eval_result": res.model_dump()
        }
        eval_results.append(case_res)

        total_correctness += res.correctness_score
        total_relevance += res.relevance_score
        total_groundedness += res.groundedness_score
        total_citation += res.citation_quality_score
        total_overall += res.overall_score

        if res.overall_score >= 0.7:
            passed_cases += 1

        # Persist each test case evaluation in DB
        db_eval = Evaluation(
            id=res.eval_id,
            run_id=res.run_id,
            groundedness_score=res.groundedness_score,
            relevance_score=res.relevance_score,
            citation_score=res.citation_quality_score,
            feedback=res.feedback,
            metrics={
                "case_id": test_case.id,
                "correctness_score": res.correctness_score,
                "overall_score": res.overall_score
            }
        )
        db.add(db_eval)

    db.commit()

    count = len(BENCHMARK_DATASET)
    summary = BenchmarkRunSummary(
        benchmark_id=benchmark_id,
        total_cases=count,
        passed_cases=passed_cases,
        avg_correctness=round(total_correctness / count, 2),
        avg_relevance=round(total_relevance / count, 2),
        avg_groundedness=round(total_groundedness / count, 2),
        avg_citation_quality=round(total_citation / count, 2),
        avg_overall_score=round(total_overall / count, 2),
        results=eval_results
    )

    return summary.model_dump()


@router.get("", response_model=list[dict[str, Any]])
async def list_evaluations(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    """List evaluation history from database."""
    evals = db.query(Evaluation).order_by(Evaluation.created_at.desc()).limit(100).all()
    return [
        {
            "eval_id": e.id,
            "run_id": e.run_id,
            "groundedness_score": e.groundedness_score,
            "relevance_score": e.relevance_score,
            "citation_quality_score": e.citation_score,
            "overall_score": e.metrics.get("overall_score") if isinstance(e.metrics, dict) else 0.0,
            "feedback": e.feedback,
            "created_at": e.created_at.isoformat() if e.created_at else None
        }
        for e in evals
    ]


@router.get("/benchmarks")
async def get_benchmarks() -> dict[str, Any]:
    """Retrieve pre-packaged evaluation benchmark datasets."""
    return {
        "count": len(BENCHMARK_DATASET),
        "test_cases": [t.model_dump() for t in BENCHMARK_DATASET]
    }
