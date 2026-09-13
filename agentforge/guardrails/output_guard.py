"""
Output Guardrails and Secret Scrubbing for AgentForge AI
"""
import re
from typing import Any

SECRET_PATTERNS = [
    (r"AIzaSy[A-Za-z0-9_-]{33}", "[REDACTED_GOOGLE_API_KEY]"),
    (r"sk-[A-Za-z0-9]{32,}", "[REDACTED_OPENAI_API_KEY]"),
    (r"Bearer\s+[A-Za-z0-9._-]{20,}", "Bearer [REDACTED_TOKEN]"),
    (r"password\s*=\s*['\"][^'\"]+['\"]", "password='[REDACTED]'"),
    (r"api_key\s*=\s*['\"][^'\"]+['\"]", "api_key='[REDACTED]'")
]

COT_MARKERS = [
    r"\(Thinking:.*?\)",
    r"<thinking>.*?</thinking>",
    r"Chain of thought:.*?(?=\n\n|\Z)"
]


class OutputGuard:
    """Sanitizes model and tool outputs to remove secrets and private CoT logs."""

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Redact secrets and private chain-of-thought rationale from text."""
        if not text:
            return ""

        sanitized = text

        # Redact secrets
        for pattern, replacement in SECRET_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        # Scrub raw chain-of-thought rationale
        for marker in COT_MARKERS:
            sanitized = re.sub(marker, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

        return sanitized.strip()

    @staticmethod
    def sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
        """Recursively sanitize string values in a dictionary."""
        sanitized_dict = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized_dict[key] = OutputGuard.sanitize_text(value)
            elif isinstance(value, dict):
                sanitized_dict[key] = OutputGuard.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized_dict[key] = [
                    OutputGuard.sanitize_text(item) if isinstance(item, str)
                    else OutputGuard.sanitize_dict(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                sanitized_dict[key] = value
        return sanitized_dict


default_output_guard = OutputGuard()
