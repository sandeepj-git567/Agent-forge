"""
Minimal Test Agent for AgentForge AI using Google ADK 2.x
"""
import sys
import google.adk as adk
from google.adk import Agent, Runner, Workflow, Context, Event
from google.adk.sessions import InMemorySessionService


def main():
    print(f"Python Version: {sys.version.split()[0]}")
    print(f"Google ADK Version: {adk.__version__}")

    # Create a minimal test agent instance using Google ADK 2.x API
    agent = Agent(
        name="test_agent",
        model="gemini-2.5-flash",
        instruction="You are a minimal verification agent for AgentForge AI.",
    )

    # Instantiate a Runner with InMemorySessionService
    session_service = InMemorySessionService()
    runner = Runner(
        app_name="agentforge_test_app",
        agent=agent,
        session_service=session_service,
    )

    print("Import and instantiation test succeeded!")
    print(f"Created Agent: {agent.name} (model: {agent.model})")
    print(f"Created Runner: {runner.app_name}")


if __name__ == "__main__":
    main()
