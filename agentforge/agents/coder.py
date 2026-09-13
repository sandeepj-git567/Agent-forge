"""
Software Engineer & Code Generation Agent for AgentForge AI using Google ADK 2.9.0
"""
from google.adk import Agent

from agentforge.config.settings import settings
from agentforge.prompts.templates import AgentPrompt
from agentforge.tools.code_analysis import safe_code_analysis

CODER_PROMPT = AgentPrompt(
    role="Software Engineer Agent",
    objective="Write clean, type-safe Python/TypeScript code and perform static AST analysis.",
    constraints=["Ensure valid syntax.", "Adhere to PEP8 / ESLint standards."],
    expected_output="Production-ready code snippets with static analysis verification.",
    tool_rules=["Use safe_code_analysis to verify syntax."],
    safety_rules=["Never generate shell execution commands or un-sanitized eval statements."]
)


def create_coder_agent() -> Agent:
    return Agent(
        name="coder",
        model=settings.DEFAULT_LLM_MODEL,
        instruction=CODER_PROMPT.compile(),
        tools=[safe_code_analysis]
    )
