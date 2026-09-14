# Security Policy & Guardrails — AgentForge AI

## Overview
AgentForge AI enforces multi-layered enterprise security controls across application configuration, authentication & RBAC, RAG pipeline ingestion, tool execution, telemetry, and automated CI/CD pipeline scans.

---

## 1. Security Architecture Matrix

| Domain | Control Mechanism | Implementation |
|---|---|---|
| **Secret Management** | Pydantic Settings v2 + Masking | `agentforge/config/settings.py` masks API keys & JWT secrets on serialization |
| **Authentication** | PBKDF2 Password Hashing + JWT | `agentforge/auth/dependencies.py` enforces signed Bearer token validation |
| **RBAC** | `require_role()` Dependency | Enforces `ADMIN`, `ENGINEER`, `USER`, and `VIEWER` permission boundaries |
| **Tool Execution SSRF Guard** | `validate_url_ssrf()` | Blocks `localhost`, `127.0.0.1`, AWS/GCP metadata APIs (`169.254.169.254`), and private subnets |
| **Tool Execution Redaction** | `redact_secrets()` | Replaces API keys, tokens, and private headers in tool outputs with `[REDACTED_SECRET]` |
| **RAG Ingestion Guards** | File Extension & Path Traversal Guards | Rejects executable file uploads (`.exe`, `.sh`, `.bat`, etc.) and path traversal patterns |
| **RAG Deduplication** | SHA-256 Content Hashing | Prevents duplicate document chunking and vector storage bloating |
| **CoT Redaction** | System Prompt Guardrail | Strictly prevents logging or returning agent `<thought>` chain-of-thought steps |
| **Audit Logging** | `AuditEvent` Database Persistence | `MetricsRecorder.log_audit_event()` persists security operations to DB |
| **CI/CD Security Scan** | Bandit Static Analysis | `.github/workflows/ci.yml` runs automated security checks on every pull request |

---

## 2. SSRF Guardrail Policy (`validate_url_ssrf`)

The `web_search` and HTTP fetch tool components intercept and validate target URLs before sending requests.

### Blocked Destinations:
- Loopback addresses (`localhost`, `127.0.0.1`, `::1`)
- Link-local cloud metadata endpoints (`169.254.169.254`)
- Private RFC 1918 subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`)

---

## 3. Secret Redaction Policy (`redact_secrets`)

All tool outputs are sanitized prior to returning context to the agent runtime or storing execution logs. Key patterns matched include:
- `AIzaSy...` (Google API Keys)
- `sk-...` (OpenAI Keys)
- `ghp_...` (GitHub Personal Access Tokens)
- `eyJ...` (JWT Tokens)
- Dictionary keys matching `password`, `secret`, `api_key`, `token`

---

## 4. Reporting Security Vulnerabilities

To report security issues or vulnerability findings, please create an issue or contact the security maintainers at `security@agentforge-ai.org`.
