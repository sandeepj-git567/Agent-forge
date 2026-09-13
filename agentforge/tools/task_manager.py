"""
In-Memory Task Management Tool for AgentForge AI
"""
from typing import Any

# In-memory task repository for Phase 1
_TASK_STORE: dict[str, dict[str, Any]] = {}


def task_management(
    action: str,
    task_id: str | None = None,
    title: str | None = None,
    assigned_agent: str | None = None,
    status: str | None = "pending"
) -> dict[str, Any]:
    """
    In-memory task management tool for workflow planning (WRITE category).
    Supported actions: 'create', 'update', 'get', 'list'.
    """
    action_clean = action.lower().strip()

    if action_clean == "create":
        if not title:
            return {"status": "error", "message": "Task title is required for create action"}
        new_id = task_id or f"task-{len(_TASK_STORE) + 1:03d}"
        task_data = {
            "task_id": new_id,
            "title": title,
            "assigned_agent": assigned_agent or "unassigned",
            "status": status or "pending"
        }
        _TASK_STORE[new_id] = task_data
        return {"status": "success", "action": "create", "task": task_data}

    elif action_clean == "update":
        if not task_id or task_id not in _TASK_STORE:
            return {"status": "error", "message": f"Task ID '{task_id}' not found"}
        if title:
            _TASK_STORE[task_id]["title"] = title
        if assigned_agent:
            _TASK_STORE[task_id]["assigned_agent"] = assigned_agent
        if status:
            _TASK_STORE[task_id]["status"] = status
        return {"status": "success", "action": "update", "task": _TASK_STORE[task_id]}

    elif action_clean == "get":
        if not task_id or task_id not in _TASK_STORE:
            return {"status": "error", "message": f"Task ID '{task_id}' not found"}
        return {"status": "success", "action": "get", "task": _TASK_STORE[task_id]}

    elif action_clean == "list":
        return {
            "status": "success",
            "action": "list",
            "tasks": list(_TASK_STORE.values()),
            "count": len(_TASK_STORE)
        }

    else:
        return {"status": "error", "message": f"Unsupported action '{action}'. Use create, update, get, or list."}
