# Docker & Multi-Stage Deployment — AgentForge AI

## Overview
AgentForge AI utilizes a multi-stage `Dockerfile` and a multi-container `docker-compose.yml` architecture combining a Node.js React frontend build, FastAPI backend runtime, and a PostgreSQL 16 database with the `pgvector` extension.

---

## 1. Containerization Architecture

```
[ Docker Compose ]
   ├── postgres (pgvector/pgvector:pg16)
   │      └── Data Volume: pgdata
   │
   └── agentforge-api (Multi-stage Build)
          ├── Stage 1: node:20-alpine (Builds React assets to dist/)
          └── Stage 2: python:3.13-slim (FastAPI server serving API + static frontend)
```

---

## 2. Dockerfile Build Stages

### Stage 1: Frontend Builder
- Base Image: `node:20-alpine`
- Installs npm packages and executes `npm run build` in `frontend/`.
- Compiles TSX code into production JavaScript and static assets (`dist/`).

### Stage 2: Production Backend Runtime
- Base Image: `python:3.13-slim`
- Installs Python backend dependencies from `requirements.txt`.
- Copies `agentforge/` backend modules and copies built static files from `frontend-builder` into `agentforge/static`.
- Exposes port `8000` and launches Uvicorn server (`agentforge.api.main:app`).

---

## 3. Deployment Instructions

### Quick Start with Docker Compose
```bash
# 1. Configure environment variables
cp .env.example .env
# Set GOOGLE_API_KEY and JWT_SECRET in .env

# 2. Build and launch services in detached mode
docker-compose up --build -d

# 3. Access applications:
# - API Swagger Docs: http://localhost:8000/docs
# - React Web Dashboard: http://localhost:8000/dashboard
```

### Standalone Docker Build & Run
```bash
# Build production image
docker build -t agentforge-ai:latest .

# Run container with SQLite fallback
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_API_KEY="your_api_key" \
  -e JWT_SECRET="your_32_character_jwt_secret" \
  --name agentforge-app \
  agentforge-ai:latest
```

---

## 4. Production Environment Variables

| Variable | Description | Required | Default |
|---|---|---|---|
| `GOOGLE_API_KEY` | Google Gemini API Key | Yes (for Gemini/ADK) | None |
| `JWT_SECRET` | Secret key for JWT Bearer token generation (min 32 chars) | Yes | Auto-fallback dev secret |
| `DATABASE_URL` | SQLAlchemy Connection URL | No | `sqlite:///:memory:` |
| `APP_ENV` | Runtime environment (`production`, `development`, `testing`) | No | `production` |
| `LOG_LEVEL` | Application logging verbosity (`INFO`, `DEBUG`, `WARNING`) | No | `INFO` |
