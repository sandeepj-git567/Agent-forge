"""
Researcher Agent Definition for AgentForge AI using Google ADK 2.9.0
"""
from google.adk import Agent

from agentforge.config.settings import settings
from agentforge.prompts.templates import RESEARCHER_PROMPT
from agentforge.tools.doc_search import document_search
from agentforge.tools.web_search import web_search


def create_researcher_agent() -> Agent:
    """Instantiate the Researcher Agent with Google ADK 2.9.0."""
    return Agent(
        name="researcher",
        model=settings.DEFAULT_LLM_MODEL,
        instruction=RESEARCHER_PROMPT.compile(),
        tools=[web_search, document_search]
    )
