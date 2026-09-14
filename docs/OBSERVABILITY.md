# Observability & Tracing — AgentForge AI

## Overview
AgentForge AI implements a comprehensive, production-grade observability architecture covering HTTP header correlation propagation, in-memory telemetry metric collection, OpenTelemetry trace instrumentation, and database-backed audit logging.

---

## 1. Observability Architecture

```
[ HTTP Client Request ]
         │ (Optional X-Correlation-ID)
         ▼
[ ProductionObservabilityMiddleware ]
         │ ├─ Generates/Propagates X-Correlation-ID
         │ ├─ Computes Latency (X-Process-Time-MS)
         │ └─ Updates TelemetryCollector Metrics
         ▼
[ FastAPI Endpoint Handlers ]
         │ ├─ OpenTelemetry Spans (MetricsRecorder.record_span)
         │ └─ DB Security Audit Logging (MetricsRecorder.log_audit_event)
         ▼
[ System Telemetry API ] (`GET /api/v1/health/metrics`)
```

---

## 2. Core Components

### `ProductionObservabilityMiddleware` (`agentforge/observability/middleware.py`)
- Automatically intercepts every incoming HTTP request.
- Extracts `X-Correlation-ID` header if present; generates a unique UUID4 string if omitted.
- Injects `X-Correlation-ID` and `X-Process-Time-MS` headers into all outgoing HTTP responses.
- Records request count, HTTP 4xx/5xx error count, and latency samples into `TelemetryCollector`.

### `TelemetryCollector` (`agentforge/observability/metrics.py`)
- In-memory metrics accumulator tracking key system operational counters:
  - `total_requests`: Aggregated HTTP request count.
  - `total_tasks_run`: Executed ADK agent tasks.
  - `total_rag_queries`: Executed RAG vector searches.
  - `total_evaluations`: Completed evaluation runs.
  - `total_errors`: HTTP 4xx/5xx errors.
  - `error_rate`: Ratio of errors to total requests.
  - `avg_latency_ms`: Rolling 1,000-sample average response latency in milliseconds.
- Accessible via API endpoint `GET /api/v1/health/metrics`.

### `MetricsRecorder` & OpenTelemetry Tracing (`agentforge/observability/tracer.py`)
- Spawns named OpenTelemetry trace spans (`MetricsRecorder.record_span(name, attributes)`).
- Provides `log_audit_event()` helper that writes structured security and administrative events to the `audit_events` database table.

---

## 3. Telemetry Endpoint Response Schema (`GET /api/v1/health/metrics`)

```json
{
  "total_requests": 142,
  "total_tasks_run": 15,
  "total_rag_queries": 28,
  "total_evaluations": 6,
  "total_errors": 0,
  "error_rate": 0.0,
  "avg_latency_ms": 14.82,
  "sample_size": 142
}
```

---

## 4. Verification

Run the observability test suite:
```bash
pytest tests/test_observability.py -v
```
