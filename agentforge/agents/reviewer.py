"""
Reviewer Agent Definition for AgentForge AI using Google ADK 2.9.0
"""
from google.adk import Agent

from agentforge.config.settings import settings
from agentforge.prompts.templates import REVIEWER_PROMPT
from agentforge.tools.code_analysis import safe_code_analysis


def create_reviewer_agent() -> Agent:
    """Instantiate the Quality & Safety Reviewer Agent with Google ADK 2.9.0."""
    return Agent(
        name="reviewer",
        model=settings.DEFAULT_LLM_MODEL,
        instruction=REVIEWER_PROMPT.compile(),
        tools=[safe_code_analysis]
    )
