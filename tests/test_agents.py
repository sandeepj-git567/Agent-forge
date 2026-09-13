"""
Tests for Agent Configurations using Google ADK 2.9.0
"""
from google.adk import Agent

from agentforge.agents.orchestrator import create_orchestrator_agent
from agentforge.agents.planner import create_planner_agent
from agentforge.agents.researcher import create_researcher_agent
from agentforge.agents.reviewer import create_reviewer_agent


def test_planner_agent_configuration():
    planner = create_planner_agent()
    assert isinstance(planner, Agent)
    assert planner.name == "planner"
    assert len(planner.tools) == 1
    assert "ROLE" in planner.instruction


def test_researcher_agent_configuration():
    researcher = create_researcher_agent()
    assert isinstance(researcher, Agent)
    assert researcher.name == "researcher"
    assert len(researcher.tools) == 2


def test_reviewer_agent_configuration():
    reviewer = create_reviewer_agent()
    assert isinstance(reviewer, Agent)
    assert reviewer.name == "reviewer"
    assert len(reviewer.tools) == 1


def test_orchestrator_agent_sub_agents():
    orchestrator = create_orchestrator_agent()
    assert isinstance(orchestrator, Agent)
    assert orchestrator.name == "root_orchestrator"
    assert len(orchestrator.sub_agents) == 3
    sub_names = [sa.name for sa in orchestrator.sub_agents]
    assert "planner" in sub_names
    assert "researcher" in sub_names
    assert "reviewer" in sub_names
