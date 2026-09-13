# AgentForge AI 🚀

**Enterprise AI Agent Orchestration, RAG, Workflow Automation & Evaluation Platform**

AgentForge AI is a production-grade GenAI engineering platform designed to orchestrate multi-agent workflows, enforce safety guardrails, manage tools, and execute task graphs using **Google ADK 2.9.0** and **FastAPI**.

---

## 1. Problem Statement

Building enterprise generative AI applications requires far more than simple LLM prompts or basic chatbots. Production AI systems require:
- Reliable multi-agent coordination (Planners, Researchers, Reviewers).
- Granular tool permissions and safety shields blocking destructive execution.
- Deterministic trace tracking without exposing private internal rationale or credentials.
- Modular architecture with clean API contracts and cloud container readiness.

## 2. Solution

AgentForge AI addresses these challenges by offering:
- **Hierarchical Multi-Agent Orchestration**: Built on Google ADK 2.9.0, coordinating specialized agents.
- **Tool Permission Engine**: Categorizes tools (`READ_ONLY`, `EXTERNAL_SEARCH`, `FILE_ANALYSIS`, `WRITE`, `DESTRUCTIVE`) and enforces explicit approval rules.
- **Comprehensive Guardrails**: Real-time input validation, prompt injection defense, secret redaction, and CoT protection.
- **RESTful API & Audit Tracing**: Asynchronous FastAPI endpoints delivering detailed execution timelines.

---

## 3. Architecture

```
User Task -> FastAPI -> Input Guardrails -> Root Agent (Google ADK 2.9.0)
                                                 |
                               +-----------------+-----------------+
                               |                 |                 |
                               v                 v                 v
                         Planner Agent    Researcher Agent   Reviewer Agent
                               |                 |                 |
                         Task Tool        Search Tools      Code Check Tool
                               |                 |                 |
                               +-----------------+-----------------+
                                                 |
                                                 v
                                         Output Guardrails -> Trace Timeline
```

---

## 4. Google ADK 2.9.0 Integration

AgentForge AI natively implements the **Google ADK 2.9.0** API:
- `Agent` & `LlmAgent` for agent definitions.
- `Runner` with `InMemorySessionService()` for stateful session execution.
- Asynchronous event streams (`Runner.run_async`) for monitoring tool calls and completion states.

---

## 5. Sub-Agents

1. **Root Orchestrator (`root_orchestrator`)**: Coordinates workflow steps and sub-agents.
2. **Planner Agent (`planner`)**: Decomposes requests into structured task graphs.
3. **Researcher Agent (`researcher`)**: Queries web and internal document databases for evidence.
4. **Reviewer Agent (`reviewer`)**: Performs static code analysis and quality verification.

---

## 6. Tool Registry & Permission System

Tools are registered in `ToolRegistry` with strict permission categories:
- `web_search`: Live search interface (`EXTERNAL_SEARCH`)
- `document_search`: In-memory doc repository query (`READ_ONLY`)
- `safe_code_analysis`: AST static Python parser (`FILE_ANALYSIS`)
- `task_management`: Workflow task graph manager (`WRITE`)

*Rule*: Destructive operations (`DESTRUCTIVE`) are automatically blocked without human approval. Arbitrary shell commands are prohibited.

---

## 7. Guardrails & Security

- **InputGuard**: Rejects empty prompts, task lengths > 4,000 chars, and dangerous command patterns (`rm -rf`, `drop table`).
- **OutputGuard**: Redacts API keys (Google/OpenAI), tokens, and strips private chain-of-thought (`<thinking>`).
- **PermissionGuard**: Enforces tool allowlists and human approval requirements.

---

## 8. API Specification

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Service health status |
| `GET` | `/api/v1/health/ready` | ADK runtime & tool readiness check |
| `POST` | `/api/v1/tasks/run` | Execute multi-agent task workflow |
| `GET` | `/api/v1/tasks/{run_id}` | Retrieve task execution trace by ID |
| `GET` | `/docs` | OpenAPI / Swagger UI |

---

## 9. Quickstart & Local Setup

```bash
# 1. Clone repository & setup virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Run FastAPI development server
uvicorn agentforge.api.main:app --reload --port 8000
```

---

## 10. Docker Deployment

```bash
docker-compose up --build
```
Access the application at `http://localhost:8000/docs`.

---

## 11. Limitations & Phase 1 Scope

- Phase 1 uses in-memory session management and document storage.
- Real RAG vector database (PostgreSQL + pgvector) will be introduced in Phase 2.

---

## 12. Roadmap

- **Phase 1**: AI Agent Foundation & Guardrails (Completed)
- **Phase 2**: Real RAG & Persistence (PostgreSQL, pgvector, Supabase, Alembic)
- **Phase 3**: Advanced Multi-Agent Task Graphs
- **Phase 4**: Visual Workflow Builder
- **Phase 5**: AI Evaluation System
