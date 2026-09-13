# Local Setup & Docker Deployment Guide

## Prerequisites

- Python 3.10+ (Current Environment: Python 3.13.7)
- Docker & Docker Compose (Optional for containerized run)

## Local Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and set GOOGLE_API_KEY if available
   ```

4. Run FastAPI development server:
   ```bash
   uvicorn agentforge.api.main:app --reload --port 8000
   ```

## Running with Docker Compose

1. Build and start the container:
   ```bash
   docker-compose up --build
   ```

2. Access endpoints:
   - FastAPI Docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/api/v1/health`
