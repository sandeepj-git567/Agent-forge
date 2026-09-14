"""
Workflow Planning Tool for AgentForge AI
"""
from typing import Any
from pydantic import BaseModel, Field


class WorkflowPlanningInput(BaseModel):
    """Pydantic input schema for workflow_planning tool."""
    goal: str = Field(..., description="Target business objective or workflow description")
    max_steps: int = Field(default=5, description="Maximum number of DAG node steps")


def workflow_planning(goal: str, max_steps: int = 5) -> dict[str, Any]:
    """
    Generate structured workflow graph plan from target goal (WRITE permission category).
    """
    goal_clean = goal.strip()
    if not goal_clean:
        return {"status": "error", "message": "Workflow planning goal cannot be empty."}

    steps = [
        {"step_id": "step-1", "title": "Analyze Goal & Requirements", "agent": "planner"},
        {"step_id": "step-2", "title": "Search Knowledge Base & Evidence", "agent": "researcher"},
        {"step_id": "step-3", "title": "Synthesize Analysis & Generate Output", "agent": "analyst"},
        {"step_id": "step-4", "title": "Review Quality & Security Audit", "agent": "reviewer"}
    ][:max_steps]

    return {
        "status": "success",
        "goal": goal_clean,
        "step_count": len(steps),
        "steps": steps,
        "is_executable": True
    }
