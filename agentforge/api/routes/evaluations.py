"""
Evaluation API Router
"""
from typing import Any

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from agentforge.eval.datasets import BENCHMARK_DATASET
from agentforge.eval.evaluator import default_evaluator

router = APIRouter(prefix="/evaluations", tags=["AI Evaluation"])

_EVAL_STORE: list[dict[str, Any]] = []


class EvaluationRequest(BaseModel):
    """Payload for POST /api/v1/evaluations/run"""
    input_text: str = Field(..., description="Original user prompt input")
    actual_output: str = Field(..., description="Actual agent output to evaluate")
    expected_output: str = Field(default="", description="Expected output criteria")


@router.post("/run", status_code=status.HTTP_201_CREATED)
async def run_evaluation(payload: EvaluationRequest) -> dict[str, Any]:
    """Execute automated evaluation on agent output."""
    res = default_evaluator.evaluate_response(
        input_text=payload.input_text,
        actual_output=payload.actual_output,
        expected_output=payload.expected_output
    )
    result_dict = res.model_dump()
    _EVAL_STORE.append(result_dict)
    return result_dict


@router.get("", response_model=list[dict[str, Any]])
async def list_evaluations() -> list[dict[str, Any]]:
    """List evaluation history."""
    return _EVAL_STORE


@router.get("/benchmarks")
async def get_benchmarks() -> dict[str, Any]:
    """Retrieve evaluation benchmark datasets."""
    return {
        "count": len(BENCHMARK_DATASET),
        "test_cases": [t.model_dump() for t in BENCHMARK_DATASET]
    }
