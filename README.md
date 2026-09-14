# AgentForge AI 🚀

**Enterprise AI Agent Orchestration, RAG, DAG Workflows, AI Evaluation & Observability Platform**

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![Google ADK 2.9.0](https://img.shields.io/badge/Google_ADK-2.9.0-green.svg)](https://github.com/google/adk)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![React Dashboard](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb.svg)](https://vitejs.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

AgentForge AI is a state-of-the-art, production-grade AI engineering platform designed to orchestrate multi-agent task graphs using **Google Agent Development Kit (ADK 2.9.0)**, **FastAPI**, **PostgreSQL / pgvector**, and an integrated **React Web Dashboard**.

---

## 📸 Platform Capabilities & Key Features

```
                                  [ Client / React Web Dashboard ]
                                                  │
                                                  ▼
                               [ ProductionObservabilityMiddleware ]
                                                  │
                       ┌──────────────────────────┴──────────────────────────┐
                       ▼                                                     ▼
        [ FastAPI REST API (/api/v1) ]                             [ Static Dashboard (/dashboard) ]
                       │
       ┌───────────────┼───────────────────────────┬─────────────────────────┐
       ▼               ▼                           ▼                         ▼
 [ ADK Runtime ]  [ RAG Pipeline ]            [ Workflow Engine ]       [ AI Evaluation ]
 (Google ADK 2.9.0) (SHA-256 / pgvector)       (DAG / Parallel Waves)    (5 Metrics / Benchmarks)
       │               │                           │                         │
       ▼               ▼                           ▼                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                            Relational & Vector Storage Layer                                │
│       Users • Documents • Chunks • Workflows • Executions • Evaluations • Audit Logs        │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔥 Enterprise Feature Matrix

### 1. 🤖 Google ADK 2.9.0 Multi-Agent Runtime
- Native implementation of Google ADK 2.9.0 `Runner` with `InMemorySessionService`.
- Coordinates specialized sub-agents: **Root Orchestrator**, **Planner**, **Researcher**, and **Reviewer**.
- Bounded retries, task cancellation handles (`POST /api/v1/tasks/{run_id}/cancel`), and execution mode reporting (`real_gemini_adk` vs `offline_fallback`).

### 2. 🧠 Enterprise RAG & Hybrid Vector Retrieval
- PostgreSQL + `pgvector` vector similarity retrieval with fallback in-memory search.
- SHA-256 document hashing for instant duplicate detection and upload prevention.
- Security ingestion guards: Blocks executable extensions (`.exe`, `.sh`, `.bat`, etc.) and path traversal patterns (`../`).
- Automatic document chunking with metadata persistence, source citation generation, and cascade document deletion (`DELETE /documents/{id}`).

### 3. ⚡ Executable DAG Workflow Engine
- Parallel wave execution using Kahn's topological sorting algorithm and `asyncio.gather`.
- Cycle dependency detection throwing `CyclicDependencyError`.
- Human-in-the-Loop (HITL) approval nodes (`requires_approval=True`) with pause/resume endpoints (`POST /workflows/approvals/{id}/approve` & `reject`).
- Real-time workflow state visualization endpoint (`GET /workflows/{id}/visualize`).

### 4. 📊 Real AI Evaluation System
- Automated metric evaluation suite:
  - **Correctness**: LLM-assisted factual accuracy evaluation.
  - **Relevance**: Semantic alignment between prompt and response.
  - **Groundedness**: Faithfulness ratio to retrieved context chunks.
  - **Citation Quality**: Validation of source references.
  - **Precision & Recall**: Context retrieval accuracy metrics.
- Pre-packaged benchmark dataset runner (`POST /evaluations/benchmark/run`) with database persistent history (`evaluations` table).

### 5. 🛡️ Security, Auth & RBAC
- Database-backed authentication (`UserRepository`) with PBKDF2 password hashing and JWT Bearer tokens.
- Role-Based Access Control (`require_role` dependency) supporting `ADMIN`, `ENGINEER`, `USER`, and `VIEWER`.
- Server-Side Request Forgery (SSRF) URL validator (`validate_url_ssrf`) blocking `localhost`, AWS/GCP metadata endpoints (`169.254.169.254`), and private RFC 1918 subnets.
- Automatic secret redactor (`redact_secrets`) scrubbing API keys, tokens, and credentials from tool outputs.
- System prompt guardrails prohibiting internal `<thought>` chain-of-thought exposure.

### 6. 👁️ Observability & Audit Logging
- `ProductionObservabilityMiddleware` propagating correlation IDs (`X-Correlation-ID`) and response latencies (`X-Process-Time-MS`).
- Telemetry collector tracking total requests, task runs, RAG queries, evaluations, error rates, and rolling average latency (`GET /api/v1/health/metrics`).
- Database security audit event logging (`MetricsRecorder.log_audit_event`).

### 7. 🖥️ Integrated React Dashboard
- Built with React 18, TypeScript, and Vite, mounted at `/dashboard`.
- Includes 10 interactive tabs: **Overview**, **Agent Task Execution**, **Knowledge RAG**, **Workflow Builder**, **AI Evaluation**, **Observability**, **Security Audit**, **API Keys**, **System Settings**, and **Documentation**.
- Real-time toast notifications and typed API client (`frontend/src/api/client.ts`).

---

## 🛠️ Complete API Reference

| Endpoint | Method | Role Required | Description |
|---|---|---|---|
| `/api/v1/health` | `GET` | Public | System operational health check |
| `/api/v1/health/ready` | `GET` | Public | Component readiness check (ADK runtime, tools) |
| `/api/v1/health/config` | `GET` | Public | Safe configuration summary (secrets masked) |
| `/api/v1/health/metrics` | `GET` | Public | Telemetry & performance metrics summary |
| `/api/v1/auth/register` | `POST` | Public | Register new user account |
| `/api/v1/auth/login` | `POST` | Public | Authenticate user & obtain JWT Bearer token |
| `/api/v1/auth/me` | `GET` | Authenticated | Retrieve current user profile |
| `/api/v1/tasks/run` | `POST` | USER | Execute multi-agent task workflow |
| `/api/v1/tasks/{run_id}` | `GET` | USER | Retrieve task execution status and trace |
| `/api/v1/tasks/{run_id}/cancel` | `POST` | ENGINEER | Cancel a running task execution |
| `/api/v1/rag/upload` | `POST` | USER | Ingest and chunk document into pgvector RAG |
| `/api/v1/rag/answer` | `POST` | USER | Execute vector search & grounded RAG answer |
| `/api/v1/documents` | `GET` | USER | List ingested knowledge documents |
| `/api/v1/documents/{id}` | `DELETE` | ENGINEER | Cascade delete document and chunks |
| `/api/v1/workflows` | `POST` | ENGINEER | Define new DAG workflow |
| `/api/v1/workflows/{id}/execute` | `POST` | USER | Run workflow execution |
| `/api/v1/workflows/approvals/{id}/approve` | `POST` | ENGINEER | Approve paused workflow node |
| `/api/v1/evaluations/run` | `POST` | ENGINEER | Evaluate single task execution |
| `/api/v1/evaluations/benchmark/run` | `POST` | ADMIN | Run benchmark evaluation suite |

---

## 💻 Quickstart & Local Setup

### 1. Prerequisites
- Python 3.13+
- Node.js 20+
- (Optional) PostgreSQL 16 with `pgvector`

### 2. Installation & Setup
```bash
# Clone repository
git clone https://github.com/sandeepj-git567/Agent-forge.git
cd Agent-forge

# Create Python virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
```

### 3. Build Frontend & Launch FastAPI Server
```bash
# Build React frontend production static bundle
cd frontend
npm install
npm run build
cd ..

# Run FastAPI backend server
uvicorn agentforge.api.main:app --reload --port 8000
```
- **Interactive OpenAPI Specs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Web Dashboard**: [http://localhost:8000/dashboard](http://localhost:8000/dashboard)

---

## 🐳 Docker Deployment

Deploy the full stack (FastAPI backend + React frontend + PostgreSQL pgvector database) with Docker Compose:

```bash
# Build and start services in detached mode
docker-compose up --build -d

# Verify container health
docker-compose ps
```

---

## 🧪 Testing & Quality Assurance

AgentForge AI maintains a **100% test pass rate** across 69 unit and integration tests.

```bash
# Execute unit & integration test suite
pytest -v
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
