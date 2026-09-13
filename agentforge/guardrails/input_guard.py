"""
Input Validation and Document Security Guardrails for AgentForge AI
"""
import os
import re
from typing import Any

from agentforge.config.settings import settings

DANGEROUS_PATTERNS = [
    r"rm\s+-rf",
    r"drop\s+database",
    r"drop\s+table",
    r"format\s+[c-z]:",
    r"eval\(",
    r"exec\(",
    r"ignore\s+all\s+previous\s+instructions",
    r"system\s+override",
    r"bypass\s+safety",
    r"cat\s+/etc/passwd",
    r"sudo\s+rm"
]

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class InputGuard:
    """Validates user task requests and uploaded files prior to processing."""

    def __init__(self, max_length: int = settings.MAX_TASK_LENGTH) -> None:
        self.max_length = max_length

    def validate_task(self, task: str) -> tuple[bool, str, dict[str, Any]]:
        """
        Validate task string for empty check, length limit, and dangerous patterns.
        """
        if not task or not task.strip():
            return False, "Task prompt cannot be empty.", {"reason": "empty_task"}

        task_clean = task.strip()

        if len(task_clean) > self.max_length:
            return False, f"Task length ({len(task_clean)} chars) exceeds maximum limit of {self.max_length}.", {
                "reason": "max_length_exceeded",
                "length": len(task_clean),
                "max_length": self.max_length
            }

        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, task_clean, re.IGNORECASE):
                return False, "Dangerous request or prompt injection attempt detected.", {
                    "reason": "dangerous_pattern_matched",
                    "pattern": pattern
                }

        return True, "", {"reason": "passed", "length": len(task_clean)}

    def validate_file_upload(self, filename: str, file_size: int) -> tuple[bool, str]:
        """
        Validate document upload filename and file size limits.
        Protects against path traversal and malicious filenames.
        """
        if not filename or not filename.strip():
            return False, "Filename cannot be empty."

        # Path traversal defense
        base_name = os.path.basename(filename)
        if base_name != filename or ".." in filename or "/" in filename or "\\" in filename:
            return False, "Malicious filename or path traversal sequence detected."

        if file_size <= 0:
            return False, "Uploaded file is empty (0 bytes)."

        if file_size > MAX_FILE_SIZE_BYTES:
            return False, f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum limit of {MAX_FILE_SIZE_BYTES / (1024*1024):.0f} MB."

        return True, ""


default_input_guard = InputGuard()
