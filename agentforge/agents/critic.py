"""
Critic & Summarizer Agents for AgentForge AI using Google ADK 2.9.0
"""
from google.adk import Agent

from agentforge.config.settings import settings
from agentforge.prompts.templates import AgentPrompt

CRITIC_PROMPT = AgentPrompt(
    role="Adversarial Critic Agent",
    objective="Identify flaws, gaps, logical fallacies, or edge cases in proposed plans and research.",
    constraints=["Be constructive and rigorous."],
    expected_output="Critique report detailing potential weaknesses and mitigation steps.",
    tool_rules=[],
    safety_rules=["Do not approve plans with safety or security gaps."]
)

SUMMARIZER_PROMPT = AgentPrompt(
    role="Executive Summarizer Agent",
    objective="Compress lengthy technical reports into executive key takeaways and action items.",
    constraints=["Preserve core facts and technical accuracy."],
    expected_output="Executive summary with bulleted action items.",
    tool_rules=[],
    safety_rules=[]
)


def create_critic_agent() -> Agent:
    return Agent(
        name="critic",
        model=settings.DEFAULT_LLM_MODEL,
        instruction=CRITIC_PROMPT.compile()
    )


def create_summarizer_agent() -> Agent:
    return Agent(
        name="summarizer",
        model=settings.DEFAULT_LLM_MODEL,
        instruction=SUMMARIZER_PROMPT.compile()
    )
