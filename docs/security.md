# Security Architecture & Audit Hardening Guide

AgentForge AI is engineered with defense-in-depth security principles.

## 1. Input & File Upload Defense
- **Path Traversal Shield**: File upload paths are stripped using `os.path.basename` and validated against directory traversal patterns (`../`).
- **File Size Limit**: Strictly capped at 10 MB per file.
- **Dangerous Command Filters**: Pattern matching detects command injection attempts (`rm -rf`, `drop table`, `eval`).

## 2. Tool Sandbox & Permission Rules
- **Permission Categorization**: `READ_ONLY`, `EXTERNAL_SEARCH`, `FILE_ANALYSIS`, `WRITE`, `DESTRUCTIVE`.
- **Destructive Operation Blocking**: Tools classified as `DESTRUCTIVE` are automatically blocked unless `has_approval=True` is provided.
- **Zero Shell Execution**: No arbitrary command execution tools exist or can be registered.

## 3. Secret Protection & Output Redaction
- Regex scanners automatically sanitize Google API keys, OpenAI API keys, Bearer tokens, and passwords prior to returning responses to clients.
- Private Chain-of-Thought (`<thinking>`) tags are scrubbed.

## 4. Auth & Role-Based Access Control
- Passwords are stored using **bcrypt** salt hashing (`passlib`).
- JWT tokens with HMAC-SHA256 signatures protect API endpoints.
- User roles: `ADMIN`, `ENGINEER`, `USER`, `VIEWER`.
