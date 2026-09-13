"""
Intent Classifier Agent for AgentForge AI Task Routing
"""
from typing import Any


class IntentClassifier:
    """Classifies incoming user tasks into execution modes and routing graphs."""

    @staticmethod
    def classify_intent(task: str) -> dict[str, Any]:
        task_lower = task.lower().strip()

        if any(w in task_lower for w in ["code", "python", "script", "function", "bug", "refactor"]):
            mode = "coding"
            recommended_agents = ["planner", "coder", "reviewer"]
        elif any(w in task_lower for w in ["research", "paper", "find", "document", "what is", "compare"]):
            mode = "research"
            recommended_agents = ["planner", "researcher", "analyst", "reviewer"]
        elif any(w in task_lower for w in ["evaluate", "benchmark", "score", "audit"]):
            mode = "evaluation"
            recommended_agents = ["planner", "critic", "reviewer"]
        else:
            mode = "general"
            recommended_agents = ["planner", "researcher", "reviewer"]

        return {
            "mode": mode,
            "recommended_agents": recommended_agents,
            "requires_human_checkpoint": "destructive" in task_lower or "delete" in task_lower
        }


default_intent_classifier = IntentClassifier()
