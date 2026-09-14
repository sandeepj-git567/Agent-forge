# Tool Execution Security & Permission Architecture

AgentForge AI enforces strict security boundaries around agent tool calling to prevent unauthorized actions, data exfiltration, SSRF attacks, and key exposure.

## 1. Tool Permission Categories

Every tool registered in `ToolRegistry` must belong to a predefined permission category:

| Category | Description | Approval Required | Risk Level |
|---|---|---|---|
| `READ_ONLY` | Read document store, inspect metadata, or query public resources. | No | LOW |
| `EXTERNAL_SEARCH` | Web search and external document fetching. | No (SSRF Guarded) | MEDIUM |
| `FILE_ANALYSIS` | Static AST code analysis, syntax checking, and file metadata extraction. | No | LOW |
| `WRITE` | Create workflow tasks, update task status, generate execution plans. | No | MEDIUM |
| `EXECUTE` | Execute code, launch background commands, run subprocesses. | Yes | HIGH |
| `DESTRUCTIVE` | Delete database records, clear vectors, drop tables, or purge storage. | **Mandatory Human-in-the-Loop** | CRITICAL |

---

## 2. Security Guardrails

### A. SSRF (Server-Side Request Forgery) Defense
All tool inputs containing URL parameters (`url`, `endpoint`, `http://`, `https://`) are automatically intercepted and validated by `validate_url_ssrf` before tool execution:
- **Blocked Targets**: `localhost`, `127.0.0.1`, `::1`, `0.0.0.0`, `169.254.169.254` (cloud metadata), `.local`, `.internal`.
- **Blocked CIDRs**: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.0.0/16`.
- **Allowed Schemes**: `http`, `https` only (blocks `file://`, `gopher://`, `dict://`).

### B. Output Secret Redaction
Tool outputs are recursively sanitized before returning results to agent execution contexts or API responses:
- API Keys (`AIza...`, `sk-...`, `tvly-...`) are masked as `[REDACTED_SECRET]`.
- Sensitive fields (`password`, `secret`, `api_key`, `authorization`, `token`, `jwt_secret`) are masked.

### C. Human-in-the-Loop Approval Gate
Tools categorized as `DESTRUCTIVE` or flagged with `requires_approval=True` cannot execute without an explicit approval token (`has_approval=True`). Unapproved execution attempts immediately return `{"status": "blocked"}`.

### D. Execution Allowlisting
Agents can be constrained with an `allowlist` of permitted tool names. Tools outside the allowlist are denied execution.

---

## 3. Registered Core Tools

1. `web_search`: Query external web sources (`EXTERNAL_SEARCH`).
2. `document_search`: Query RAG vector store (`READ_ONLY`).
3. `safe_code_analysis`: Static AST Python security audit (`FILE_ANALYSIS`).
4. `task_management`: In-memory task state tracking (`WRITE`).
5. `workflow_planning`: Generate structured DAG workflow plans (`WRITE`).
