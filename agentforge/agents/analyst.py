"""
Data & Systems Analyst Agent for AgentForge AI using Google ADK 2.9.0
"""
from google.adk import Agent

from agentforge.config.settings import settings
from agentforge.prompts.templates import AgentPrompt

ANALYST_PROMPT = AgentPrompt(
    role="Data & Systems Analyst Agent",
    objective="Analyze data patterns, evaluate trade-offs, and synthesize quantitative/qualitative metrics.",
    constraints=["Base analysis strictly on verified input evidence.", "Quantify metrics wherever possible."],
    expected_output="Structured analytical report with key metrics and risk assessments.",
    tool_rules=["Use document_search for knowledge queries."],
    safety_rules=["Do not fabricate data or metrics."]
)


def create_analyst_agent() -> Agent:
    return Agent(
        name="analyst",
        model=settings.DEFAULT_LLM_MODEL,
        instruction=ANALYST_PROMPT.compile()
    )
