"""
Workflow and WorkflowExecution Repository
"""
from typing import Sequence
from sqlalchemy.orm import Session
from agentforge.db.models import Workflow, WorkflowExecution, ApprovalRequest


class WorkflowRepository:
    """Repository handling CRUD operations for Workflows, Executions, and Approvals."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_workflow(self, workflow_id: str, owner_id: str | None = None) -> Workflow | None:
        """Get workflow by ID with optional owner filter."""
        query = self.db.query(Workflow).filter(Workflow.id == workflow_id)
        if owner_id:
            query = query.filter(Workflow.owner_id == owner_id)
        return query.first()

    def create_workflow(
        self,
        name: str,
        graph_definition: dict,
        description: str | None = None,
        owner_id: str | None = None
    ) -> Workflow:
        """Create and persist a new workflow definition."""
        wf = Workflow(
            name=name,
            description=description,
            graph_definition=graph_definition,
            owner_id=owner_id
        )
        self.db.add(wf)
        self.db.commit()
        self.db.refresh(wf)
        return wf

    def list_workflows(self, owner_id: str | None = None, limit: int = 100) -> Sequence[Workflow]:
        """List active workflows."""
        query = self.db.query(Workflow).filter(Workflow.is_active == True)
        if owner_id:
            query = query.filter(Workflow.owner_id == owner_id)
        return query.order_by(Workflow.created_at.desc()).limit(limit).all()

    def create_execution(
        self,
        workflow_id: str,
        inputs: dict,
        user_id: str | None = None
    ) -> WorkflowExecution:
        """Create a new WorkflowExecution tracking record."""
        ex = WorkflowExecution(
            workflow_id=workflow_id,
            user_id=user_id,
            status="running",
            inputs=inputs
        )
        self.db.add(ex)
        self.db.commit()
        self.db.refresh(ex)
        return ex

    def get_execution(self, execution_id: str, user_id: str | None = None) -> WorkflowExecution | None:
        """Get workflow execution record by ID."""
        query = self.db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id)
        if user_id:
            query = query.filter(WorkflowExecution.user_id == user_id)
        return query.first()

    def update_execution_status(
        self,
        execution_id: str,
        status: str,
        node_states: dict | None = None,
        outputs: dict | None = None,
        error_details: str | None = None
    ) -> WorkflowExecution | None:
        """Update status and node state details for a workflow execution."""
        ex = self.get_execution(execution_id)
        if ex:
            ex.status = status
            if node_states is not None:
                ex.node_states = node_states
            if outputs is not None:
                ex.outputs = outputs
            if error_details:
                ex.error_details = error_details
            self.db.commit()
            self.db.refresh(ex)
        return ex

    def create_approval_request(
        self,
        execution_id: str | None,
        run_id: str | None,
        tool_name: str,
        risk_level: str = "DESTRUCTIVE",
        request_payload: dict | None = None
    ) -> ApprovalRequest:
        """Create a pending approval request for a high-risk tool execution."""
        req = ApprovalRequest(
            execution_id=execution_id,
            run_id=run_id,
            tool_name=tool_name,
            risk_level=risk_level,
            status="pending",
            request_payload=request_payload or {}
        )
        self.db.add(req)
        self.db.commit()
        self.db.refresh(req)
        return req
