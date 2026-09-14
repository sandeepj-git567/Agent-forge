# Supabase PostgreSQL & Database Setup Guide

This guide details how to configure PostgreSQL persistence and pgvector extension support for **AgentForge AI** using Supabase or any standard PostgreSQL instance.

---

## 1. Prerequisites & Environment Setup

AgentForge AI uses SQLAlchemy 2.x and Alembic for relational database persistence.

### Required Environment Variables
Set the connection strings in your `.env` file:

```env
# Runtime connection URL (uses connection pooling if enabled)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Direct connection URL (used by Alembic migrations when poolers block DDL)
DIRECT_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

> **Security Warning**: Never commit real database passwords or project reference keys to git. Keep `.env` listed in `.gitignore`.

---

## 2. Enabling pgvector on Supabase

To enable vector similarity search on Supabase:

1. Open your Supabase Project Dashboard.
2. Navigate to **Database** -> **Extensions**.
3. Search for `vector` (`pgvector`).
4. Click **Enable Extension**.

Alternatively, run the SQL command in the Supabase SQL Editor:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## 3. Database Health Check & Status Verification

Verify database connectivity and pgvector readiness via the API:

```powershell
curl -X GET "http://localhost:8000/api/v1/health/config"
```

Sample output:
```json
{
  "app_name": "AgentForge AI",
  "providers": {
    "postgresql_configured": true,
    "local_embedding_active": false
  }
}
```

---

## 4. Local Development Fallback

If `DATABASE_URL` is omitted, AgentForge AI automatically falls back to an in-memory SQLite database (`sqlite:///:memory:`) for fast zero-configuration testing.
