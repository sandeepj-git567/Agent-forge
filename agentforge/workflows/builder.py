"""
Workflow Creation Engine and Architectural Visualizer Generator for AgentForge AI
"""
from typing import Any

from agentforge.agents.classifier import default_intent_classifier
from agentforge.workflows.task_graph import TaskGraph, default_workflow_builder


class WorkflowGenerator:
    """Generates structured workflow definitions and visual diagrams from natural language prompts."""

    @staticmethod
    def generate_workflow_definition(prompt: str) -> dict[str, Any]:
        """Convert natural language workflow prompt into complete workflow JSON structure."""
        intent = default_intent_classifier.classify_intent(prompt)
        mode = intent["mode"]

        graph: TaskGraph = default_workflow_builder.build_graph_for_mode(
            workflow_name=f"Workflow_{mode.capitalize()}",
            mode=mode
        )

        steps_json = [s.model_dump() for s in graph.steps]

        diagram_mermaid = WorkflowGenerator.generate_mermaid_diagram(graph)
        diagram_ascii = WorkflowGenerator.generate_ascii_diagram(graph)

        return {
            "workflow_name": graph.workflow_name,
            "description": prompt,
            "mode": mode,
            "recommended_agents": intent["recommended_agents"],
            "steps": steps_json,
            "visualizations": {
                "mermaid": diagram_mermaid,
                "ascii": diagram_ascii
            }
        }

    @staticmethod
    def generate_mermaid_diagram(graph: TaskGraph) -> str:
        """Generate Mermaid.js flowchart string from TaskGraph."""
        lines = ["graph TD", "  User([User Goal]) --> Step_Plan[Planner Agent]"]
        for step in graph.steps:
            node_id = f"Step_{step.id}"
            lines.append(f"  {node_id}[{step.agent.capitalize()}: {step.action}]")
            for dep in step.depends_on:
                lines.append(f"  Step_{dep} --> {node_id}")
        lines.append(f"  Step_{graph.steps[-1].id} --> Output([Final Output])")
        return "\n".join(lines)

    @staticmethod
    def generate_ascii_diagram(graph: TaskGraph) -> str:
        """Generate ASCII text architecture flow diagram."""
        seq = " -> ".join([s.agent.upper() for s in graph.steps])
        return f"[USER GOAL] -> {seq} -> [FINAL OUTPUT]"


default_workflow_generator = WorkflowGenerator()
