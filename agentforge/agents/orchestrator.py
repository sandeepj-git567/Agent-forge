"""
Root Orchestrator Agent Definition for AgentForge AI using Google ADK 2.9.0
"""
from google.adk import Agent

from agentforge.agents.planner import create_planner_agent
from agentforge.agents.researcher import create_researcher_agent
from agentforge.agents.reviewer import create_reviewer_agent
from agentforge.config.settings import settings
from agentforge.prompts.templates import ROOT_ORCHESTRATOR_PROMPT


def create_orchestrator_agent() -> Agent:
    """
    Instantiate the Root Orchestrator Agent with specialized sub-agents using Google ADK 2.9.0.
    """
    planner = create_planner_agent()
    researcher = create_researcher_agent()
    reviewer = create_reviewer_agent()

    return Agent(
        name="root_orchestrator",
        model=settings.DEFAULT_LLM_MODEL,
        instruction=ROOT_ORCHESTRATOR_PROMPT.compile(),
        sub_agents=[planner, researcher, reviewer]
    )
