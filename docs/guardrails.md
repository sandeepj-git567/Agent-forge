# Safety Guardrails Specification

AgentForge AI enforces multi-layered guardrails at the input, tool, output, and trace levels.

## 1. Input Guardrails (`InputGuard`)
- **Empty Task Validation**: Tasks must contain non-whitespace text.
- **Maximum Length Enforcement**: Tasks exceeding 4,000 characters are rejected with a structured error.
- **Dangerous Keyword Detection**: Pattern matching blocks command injection, shell wipe commands (`rm -rf`), database drop commands, and system override attempts.
- **Prompt Injection Defense**: Detects adversarial directives attempting to bypass system instructions.

## 2. Permission Guardrails (`PermissionGuard`)
- **Category Enforcement**: Prevents unauthorized execution of sensitive tools.
- **Destructive Operation Shield**: Tools tagged `DESTRUCTIVE` are immediately blocked unless `has_approval=True` is provided.

## 3. Output Guardrails (`OutputGuard`)
- **Secret Redaction**: Regex patterns scan all outgoing outputs and redact Google API keys, OpenAI API keys, Bearer tokens, and passwords.
- **Chain-of-Thought Protection**: Strips internal `<thinking>` tags or raw reasoning chains prior to returning responses to client.
