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
        Validate document upload filename, extension, and file size limits.
        Protects against path traversal, executable uploads, and malicious filenames.
        """
        if not filename or not filename.strip():
            return False, "Filename cannot be empty."

        clean_name = filename.strip()

        # Path traversal defense
        base_name = os.path.basename(clean_name)
        if base_name != clean_name or ".." in clean_name or "/" in clean_name or "\\" in clean_name:
            return False, "Malicious filename or path traversal sequence detected."

        # Executable & suspicious file extension checks
        forbidden_extensions = {
            ".exe", ".dll", ".bat", ".cmd", ".sh", ".ps1", ".py", ".js",
            ".vbs", ".jar", ".php", ".asp", ".aspx", ".cgi", ".pl", ".rb",
            ".msi", ".scr", ".com", ".pif", ".application", ".gadget"
        }
        
        lower_name = clean_name.lower()
        for ext in forbidden_extensions:
            if lower_name.endswith(ext) or f"{ext}." in lower_name:
                return False, f"Executable file extension '{ext}' is strictly prohibited."

        # Allowed document extensions check
        allowed_extensions = {".pdf", ".docx", ".txt", ".md", ".markdown"}
        ext = os.path.splitext(lower_name)[1]
        if ext not in allowed_extensions:
            return False, f"Unsupported file extension '{ext}'. Supported formats: PDF, DOCX, TXT, Markdown."

        if file_size <= 0:
            return False, "Uploaded file is empty (0 bytes)."

        if file_size > MAX_FILE_SIZE_BYTES:
            return False, f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum limit of {MAX_FILE_SIZE_BYTES / (1024*1024):.0f} MB."

        return True, ""



import ipaddress
import socket
import urllib.parse


def validate_url_ssrf(url_str: str) -> tuple[bool, str]:
    """
    Validate target URL against Server-Side Request Forgery (SSRF) vulnerabilities.
    Blocks localhost, private IP subnets (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16),
    loopback (127.0.0.0/8), AWS cloud metadata (169.254.169.254), and non-HTTP protocols.
    """
    if not url_str or not isinstance(url_str, str):
        return True, ""

    try:
        parsed = urllib.parse.urlparse(url_str.strip())
    except Exception:
        return False, "Invalid URL structure."

    if parsed.scheme not in ("http", "https"):
        return False, f"Prohibited URL scheme '{parsed.scheme}'. Only http and https are allowed."

    hostname = parsed.hostname
    if not hostname:
        return False, "URL missing valid hostname."

    hostname_lower = hostname.lower()
    blocked_hosts = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "169.254.169.254", "instance-data"}
    if hostname_lower in blocked_hosts or hostname_lower.endswith(".local") or hostname_lower.endswith(".internal"):
        return False, f"Access to private/local host '{hostname}' is strictly prohibited (SSRF Guardrail)."

    # Resolve IP address to check CIDR ranges
    try:
        ip_addr = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(ip_addr)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
            return False, f"Target IP '{ip_addr}' resolves to a private or reserved network range (SSRF Guardrail)."
    except socket.gaierror:
        # Unable to resolve domain (could be offline or fake hostname in unit tests)
        pass

    return True, ""


SECRET_PATTERNS = [
    (re.compile(r"AIza[0-9A-Za-z-_]{35}"), "[REDACTED_GEMINI_KEY]"),
    (re.compile(r"sk-[0-9A-Za-z]{32,}"), "[REDACTED_API_KEY]"),
    (re.compile(r"tvly-[0-9A-Za-z]{20,}"), "[REDACTED_TAVILY_KEY]"),
    (re.compile(r"bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", re.IGNORECASE), "Bearer [REDACTED_TOKEN]"),
]

SENSITIVE_FIELD_NAMES = {"password", "secret", "api_key", "authorization", "token", "private_key", "jwt_secret"}


def redact_secrets(val: Any) -> Any:
    """
    Recursively sanitize objects, dictionaries, strings, and lists to redact sensitive API keys and tokens.
    """
    if isinstance(val, str):
        redacted_str = val
        for pattern, replacement in SECRET_PATTERNS:
            redacted_str = pattern.sub(replacement, redacted_str)
        return redacted_str
    elif isinstance(val, dict):
        new_dict = {}
        for k, v in val.items():
            if isinstance(k, str) and k.lower() in SENSITIVE_FIELD_NAMES:
                new_dict[k] = "[REDACTED_SECRET]"
            else:
                new_dict[k] = redact_secrets(v)
        return new_dict
    elif isinstance(val, list):
        return [redact_secrets(item) for item in val]
    return val


default_input_guard = InputGuard()

