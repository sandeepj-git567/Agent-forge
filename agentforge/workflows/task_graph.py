"""
Task Graph Execution Engine for AgentForge AI Multi-Agent Workflows
"""
import uuid
from typing import Any

from pydantic import BaseModel, Field


class WorkflowStep(BaseModel):
    """Single step in a task graph execution workflow."""
    id: str = Field(..., description="Unique step identifier")
    agent: str = Field(..., description="Target agent assigned to step")
    action: str = Field(..., description="Action description")
    depends_on: list[str] = Field(default_factory=list, description="Step IDs that must complete prior to this step")
    requires_approval: bool = Field(default=False, description="Whether human checkpoint is required")
    status: str = Field(default="pending")  # pending, in_progress, completed, failed, blocked
    result: dict[str, Any] | None = Field(default=None)


class TaskGraph(BaseModel):
    """Structured Multi-Agent Task Graph Model."""
    graph_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_name: str = Field(..., description="Name of the workflow")
    steps: list[WorkflowStep] = Field(default_factory=list)
    status: str = Field(default="created")

    def add_step(self, step: WorkflowStep) -> None:
        self.steps.append(step)

    def get_executable_steps(self) -> list[WorkflowStep]:
        """Return steps whose dependencies have completed and are ready to execute."""
        completed_ids = {s.id for s in self.steps if s.status == "completed"}
        executable = []
        for step in self.steps:
            if step.status == "pending" and all(dep in completed_ids for dep in step.depends_on):
                executable.append(step)
        return executable

    def is_complete(self) -> bool:
        """Return True if all steps are completed."""
        return all(s.status == "completed" for s in self.steps)


class WorkflowBuilderEngine:
    """Engine for creating task graphs from intent mode and agent definitions."""

    @staticmethod
    def build_graph_for_mode(workflow_name: str, mode: str) -> TaskGraph:
        graph = TaskGraph(workflow_name=workflow_name)

        if mode == "coding":
            graph.add_step(WorkflowStep(id="plan", agent="planner", action="Design software architecture"))
            graph.add_step(WorkflowStep(id="code", agent="coder", action="Generate source code", depends_on=["plan"]))
            graph.add_step(WorkflowStep(id="review", agent="reviewer", action="Run security and AST code checks", depends_on=["code"]))
        elif mode == "research":
            graph.add_step(WorkflowStep(id="plan", agent="planner", action="Formulate research strategy"))
            graph.add_step(WorkflowStep(id="research", agent="researcher", action="Gather web and document evidence", depends_on=["plan"]))
            graph.add_step(WorkflowStep(id="analysis", agent="analyst", action="Synthesize analytical report", depends_on=["research"]))
            graph.add_step(WorkflowStep(id="review", agent="reviewer", action="Validate facts and compliance", depends_on=["analysis"]))
        else:  # general
            graph.add_step(WorkflowStep(id="plan", agent="planner", action="Plan goal decomposition"))
            graph.add_step(WorkflowStep(id="research", agent="researcher", action="Gather context info", depends_on=["plan"]))
            graph.add_step(WorkflowStep(id="review", agent="reviewer", action="Review and validate result", depends_on=["research"]))

        return graph


default_workflow_builder = WorkflowBuilderEngine()
