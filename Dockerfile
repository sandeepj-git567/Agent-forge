# Multi-stage Dockerfile for AgentForge AI (FastAPI Backend + Production Frontend)

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python Backend
FROM python:3.13-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application backend & built frontend static assets
COPY agentforge/ /app/agentforge/
COPY tests/ /app/tests/
COPY --from=frontend-builder /app/frontend/dist /app/agentforge/static

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "agentforge.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
