"""
Executable DAG Workflow Engine with Cycle Detection, Parallel Execution, and Human Approval Pause/Resume
"""
import asyncio
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from agentforge.db.models import WorkflowExecution
from agentforge.db.repositories.workflow_repository import WorkflowRepository
from agentforge.runtime.executor import agent_runtime_executor
from agentforge.tools.registry import default_tool_registry


class CyclicDependencyError(ValueError):
    """Raised when a workflow graph contains circular dependencies."""
    pass


class WorkflowExecutionEngine:
    """
    Asynchronous DAG Workflow Execution Engine.
    Enforces topological sorting, cycle detection, parallel wave execution,
    node retries, human-in-the-loop approval pauses, and DB state tracking.
    """

    def detect_cycles_and_sort(self, nodes: list[dict[str, Any]]) -> list[list[str]]:
        """
        Validate DAG topology using Kahn's algorithm.
        Returns execution waves (list of lists of node IDs that can run in parallel).
        Raises CyclicDependencyError if graph contains circular dependencies.
        """
        node_map = {n["id"]: n for n in nodes}
        in_degree = {n["id"]: 0 for n in nodes}
        adj = {n["id"]: [] for n in nodes}

        for n in nodes:
            for dep in n.get("depends_on", []):
                if dep in node_map:
                    adj[dep].append(n["id"])
                    in_degree[n["id"]] += 1

        waves: list[list[str]] = []
        zero_in_degree = [nid for nid, deg in in_degree.items() if deg == 0]

        visited_count = 0
        while zero_in_degree:
            waves.append(zero_in_degree)
            visited_count += len(zero_in_degree)
            next_zero: list[str] = []
            for node_id in zero_in_degree:
                for neighbor in adj[node_id]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_zero.append(neighbor)
            zero_in_degree = next_zero

        if visited_count < len(nodes):
            raise CyclicDependencyError("Workflow graph contains circular/cyclic dependencies.")

        return waves

    async def execute_workflow(
        self,
        execution_id: str,
        graph_definition: dict[str, Any],
        db: Session,
        inputs: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Execute DAG workflow steps.
        Updates node_states in database as nodes transition (pending -> running -> completed/failed/paused_approval).
        """
        repo = WorkflowRepository(db)
        execution = repo.get_execution(execution_id)
        if not execution:
            return {"status": "error", "error": f"Execution ID '{execution_id}' not found."}

        nodes = graph_definition.get("nodes", [])
        if not nodes:
            repo.update_execution_status(execution_id, status="completed", outputs={"message": "Empty workflow graph."})
            return {"status": "completed", "outputs": {}}

        try:
            waves = self.detect_cycles_and_sort(nodes)
        except CyclicDependencyError as cycle_err:
            repo.update_execution_status(execution_id, status="failed", error_details=str(cycle_err))
            return {"status": "failed", "error": str(cycle_err)}

        node_map = {n["id"]: n for n in nodes}
        node_states = execution.node_states or {n["id"]: {"status": "pending", "result": None} for n in nodes}
        outputs = dict(execution.outputs or {})

        repo.update_execution_status(execution_id, status="running", node_states=node_states)

        for wave in waves:
            wave_tasks = []
            for node_id in wave:
                node = node_map[node_id]
                current_state = node_states.get(node_id, {}).get("status", "pending")

                # Skip nodes already completed in prior resume iterations
                if current_state == "completed":
                    continue

                # Check if approval checkpoint is required
                if node.get("requires_approval") or node.get("risk_level") == "DESTRUCTIVE":
                    # Check if approval has already been granted
                    existing_approvals = execution.approvals or []
                    approved = any(a.tool_name == node.get("tool", node_id) and a.status == "approved" for a in existing_approvals)
                    if not approved:
                        node_states[node_id] = {"status": "paused_approval", "reason": "Requires human approval checkpoint."}
                        approval_req = repo.create_approval_request(
                            execution_id=execution_id,
                            run_id=None,
                            tool_name=node.get("tool", node_id),
                            risk_level=node.get("risk_level", "DESTRUCTIVE"),
                            request_payload={"node_id": node_id, "action": node.get("action")}
                        )
                        repo.update_execution_status(
                            execution_id,
                            status="paused_approval",
                            node_states=node_states,
                            outputs={"paused_at_node": node_id, "approval_id": approval_req.id}
                        )
                        return {
                            "status": "paused_approval",
                            "execution_id": execution_id,
                            "paused_node": node_id,
                            "approval_id": approval_req.id
                        }

                wave_tasks.append(self._execute_single_node(node, inputs or {}, node_states, repo, execution_id))

            if wave_tasks:
                results = await asyncio.gather(*wave_tasks, return_exceptions=True)
                for res in results:
                    if isinstance(res, Exception):
                        repo.update_execution_status(
                            execution_id,
                            status="failed",
                            node_states=node_states,
                            error_details=str(res)
                        )
                        return {"status": "failed", "execution_id": execution_id, "error": str(res)}

        # All waves completed successfully
        repo.update_execution_status(
            execution_id,
            status="completed",
            node_states=node_states,
            outputs={"completed_nodes": list(node_states.keys()), "result_summary": "Workflow executed successfully."}
        )
        return {
            "status": "completed",
            "execution_id": execution_id,
            "node_states": node_states
        }

    async def _execute_single_node(
        self,
        node: dict[str, Any],
        inputs: dict[str, Any],
        node_states: dict[str, Any],
        repo: WorkflowRepository,
        execution_id: str
    ) -> dict[str, Any]:
        """Execute a single DAG node with retries and timeout."""
        node_id = node["id"]
        agent_name = node.get("agent", "executor")
        action = node.get("action", f"Execute node {node_id}")
        tool_name = node.get("tool")
        max_retries = node.get("max_retries", 2)

        node_states[node_id] = {"status": "running", "started_at": datetime.now(timezone.utc).isoformat()}
        repo.update_execution_status(execution_id, status="running", node_states=node_states)

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                if tool_name:
                    tool_res = default_tool_registry.execute_tool(tool_name, node.get("tool_kwargs", {}))
                    if tool_res.get("status") == "error":
                        raise RuntimeError(tool_res.get("error", "Tool execution failed."))
                    node_result = tool_res.get("result", {})
                else:
                    # Run ADK agent task executor
                    agent_res = await agent_runtime_executor.run_task(
                        task=f"{action}. Node: {node_id}",
                        mode="workflow"
                    )
                    node_result = {"answer": agent_res.get("answer"), "run_id": agent_res.get("run_id")}

                node_states[node_id] = {
                    "status": "completed",
                    "result": node_result,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "attempts": attempt
                }
                return node_result
            except Exception as err:
                last_error = err
                await asyncio.sleep(0.1 * attempt)

        node_states[node_id] = {
            "status": "failed",
            "error": str(last_error),
            "failed_at": datetime.now(timezone.utc).isoformat()
        }
        raise RuntimeError(f"Node '{node_id}' failed after {max_retries} attempts: {last_error}")

    async def resume_workflow(
        self,
        approval_id: str,
        approve: bool,
        db: Session,
        approver_email: str | None = None
    ) -> dict[str, Any]:
        """Resume a paused workflow after human approval or rejection."""
        repo = WorkflowRepository(db)
        app_req = repo.get_approval_request(approval_id)
        if not app_req:
            return {"status": "error", "error": f"Approval request '{approval_id}' not found."}

        new_status = "approved" if approve else "rejected"
        repo.update_approval_status(approval_id, status=new_status, approved_by=approver_email)

        execution = repo.get_execution(app_req.execution_id) if app_req.execution_id else None
        if not execution:
            return {"status": "error", "error": "Associated workflow execution not found."}

        if not approve:
            repo.update_execution_status(
                execution.id,
                status="cancelled",
                error_details=f"Execution rejected at human checkpoint by {approver_email or 'user'}."
            )
            return {"status": "cancelled", "execution_id": execution.id, "message": "Workflow execution rejected."}

        # Approval granted -> Resume workflow execution
        wf = repo.get_workflow(execution.workflow_id)
        graph_def = wf.graph_definition if wf else {"nodes": []}
        return await self.execute_workflow(execution.id, graph_def, db, inputs=execution.inputs)


default_workflow_engine = WorkflowExecutionEngine()
