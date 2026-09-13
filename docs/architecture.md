# AgentForge AI — Architecture Blueprint

## System Overview

AgentForge AI is an enterprise-grade AI agent orchestration, workflow automation, and evaluation platform built on **Google ADK 2.9.0** and **FastAPI**.

```
                           +------------------------+
                           |   Client / API User    |
                           +-----------+------------+
                                       |
                                       v
                           +------------------------+
                           |  FastAPI Gateway Layer |
                           |  (/api/v1/tasks/run)   |
                           +-----------+------------+
                                       |
                                       v
                           +------------------------+
                           |     Input Guardrails   |
                           | (Validation & Safety)  |
                           +-----------+------------+
                                       |
                                       v
                           +------------------------+
                           | Root Orchestrator Agent|
                           |   (Google ADK 2.9.0)   |
                           +-----+-----------+------+
                                 |           |
            +--------------------+           +--------------------+
            |                                                     |
            v                                                     v
+-----------------------+                             +-----------------------+
|     Planner Agent     |                             |   Researcher Agent    |
+-----------+-----------+                             +-----------+-----------+
            |                                                     |
            v                                                     v
+-----------------------+                             +-----------------------+
|  Task Manager Tool    |                             |  Web / Doc Tools      |
+-----------------------+                             +-----------------------+
            |                                                     |
            +--------------------+           +--------------------+
                                 |           |
                                 v           v
                           +------------------------+
                           |     Reviewer Agent     |
                           | (Safe Code & QA Check) |
                           +-----------+------------+
                                       |
                                       v
                           +------------------------+
                           |   Output Guardrails    |
                           |  (Scrubbing & Redact)  |
                           +-----------+------------+
                                       |
                                       v
                           +------------------------+
                           |    Execution Trace     |
                           +------------------------+
```

## Layer Architecture

1. **API Gateway Layer (`agentforge/api`)**:
   - Built on FastAPI with Pydantic validation schemas.
   - Exposes RESTful endpoints for task execution, readiness, health check, and execution trace retrieval.

2. **Guardrail Subsystem (`agentforge/guardrails`)**:
   - **InputGuard**: Rejects empty tasks, length overruns, and dangerous request patterns/prompt injection.
   - **OutputGuard**: Sanitizes secrets (Google/OpenAI API keys, tokens) and strips raw chain-of-thought rationale.
   - **PermissionGuard**: Validates tool authorization level and blocks destructive operations without explicit approval.

3. **Agent Orchestration (`agentforge/agents` & `agentforge/runtime`)**:
   - Root Orchestrator delegates sub-tasks across specialized ADK 2.9.0 agents (`planner`, `researcher`, `reviewer`).
   - Uses `Runner` and `InMemorySessionService` to manage execution sessions and event streaming.

4. **Tool Registry (`agentforge/tools`)**:
   - Categorizes all tools into permissions (`READ_ONLY`, `EXTERNAL_SEARCH`, `FILE_ANALYSIS`, `WRITE`, `DESTRUCTIVE`).
