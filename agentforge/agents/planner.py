"""
Planner Agent Definition for AgentForge AI using Google ADK 2.9.0
"""
from google.adk import Agent

from agentforge.config.settings import settings
from agentforge.prompts.templates import PLANNER_PROMPT
from agentforge.tools.task_manager import task_management


def create_planner_agent() -> Agent:
    """Instantiate the Planner Agent with Google ADK 2.9.0."""
    return Agent(
        name="planner",
        model=settings.DEFAULT_LLM_MODEL,
        instruction=PLANNER_PROMPT.compile(),
        tools=[task_management]
    )
