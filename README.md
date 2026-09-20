# AI Guardian — LLM Observability & Cost Intelligence Platform

> A full-stack observability prototype for tracking LLM latency, token usage, estimated cost, failures, heuristic quality signals, alerts, and multi-step workflow traces.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite)

---

## Overview

LLM-powered applications often expose only the final response:

```text
prompt → model → response
```

For development and evaluation, that is not enough. Teams also need visibility into latency, token consumption, estimated cost, failures, workflow steps, and changes in response behavior.

**AI Guardian** is a full-stack LLM observability platform that captures structured telemetry from AI applications through a reusable Python SDK, processes it with FastAPI, stores it in PostgreSQL, and visualizes it in a React dashboard.

The platform tracks:

- model and request metadata
- prompts and generated outputs
- prompt, completion, and total token usage
- request latency
- estimated API cost
- success and failure status
- heuristic quality, groundedness, and hallucination-risk signals
- operational alerts
- session and trace identifiers
- aggregated multi-step workflow traces

---

## System Architecture

```text
┌───────────────────────────────────────────────────────────────┐
│                       AI Application                          │
│      Chatbot / RAG Pipeline / Agent / Summarizer             │
└──────────────────────────┬────────────────────────────────────┘
                           │ instrumented calls
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                     AI Guardian SDK                           │
│  • @track_llm_call decorator                                 │
│  • start_trace() / log_event() / end_trace()                 │
│  • OpenAI and LangChain examples                             │
│  • background event delivery                                 │
└──────────────────────────┬────────────────────────────────────┘
                           │ HTTP telemetry
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                           │
│                                                               │
│   Event Ingestion   Cost Estimation   Heuristic Evaluation   │
│   Alerting          Metrics           Trace Aggregation       │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                     PostgreSQL                                │
│            llm_events | alerts | traces                       │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────────┐
│                  React + Vite Dashboard                       │
│        Dashboard | Events | Alerts | Traces                   │
└───────────────────────────────────────────────────────────────┘
```

---

## Key Features

### Structured LLM Event Tracking

Each instrumented interaction can record:

- input prompt
- model name and version
- generated output
- latency
- prompt, completion, and total tokens
- estimated cost
- finish reason
- request success or failure
- session ID
- user ID
- trace ID
- custom tags

Events are persisted in PostgreSQL and exposed through the REST API for filtering and analysis.

### Background Telemetry Delivery

The SDK sends event telemetry on a small background thread pool so observability requests do not block the host LLM call.

Telemetry delivery is **best effort**: network or backend failures are caught and logged instead of crashing the monitored application.

### Cost Intelligence

The backend estimates request cost from prompt and completion token counts using the configured per-model pricing table.

Metrics endpoints aggregate cost across stored events, including:

- total estimated cost
- cost by model
- total token consumption
- request counts by model

> Provider pricing changes over time. The pricing table should be reviewed before using these estimates for billing or financial reporting.

### Heuristic Response Signals

The current evaluation layer intentionally uses lightweight deterministic heuristics rather than additional LLM calls.

It produces three experimental signals:

- **Quality score** — basic response-length and refusal-pattern checks
- **Hallucination-risk indicator** — flags selected overconfident language patterns
- **Groundedness indicator** — detects simple textual grounding cues such as “according to” or “based on”

These values are **diagnostic heuristics, not factual verification**. They provide an inexpensive baseline that can later be replaced by LLM-as-judge, embedding-based, or source-grounded evaluation.

### Operational Alerting

Incoming events are checked against configurable thresholds for:

| Condition | Default |
|---|---:|
| High latency | > 5000 ms |
| High request cost | > $0.10 |
| Low quality score | < 0.4 |
| High heuristic hallucination-risk score | > 0.7 |
| Failed request | Any failure |

Thresholds can be overridden with environment variables:

```bash
ALERT_LATENCY_MS=5000
ALERT_COST_USD=0.10
ALERT_QUALITY_MIN=0.4
ALERT_HALLUCINATION_RISK=0.7
```

Alerts are persisted, displayed in the dashboard, and can be resolved through the API or UI.

### Persistent Multi-Step Tracing

AI Guardian groups related events under a shared `trace_id` for workflows such as RAG pipelines and agent chains.

```text
User Request
     ↓
Retrieval
     ↓
Reranking
     ↓
Generation
     ↓
Evaluation
```

`start_trace()` creates a persistent trace record. `log_event()` associates workflow steps with that trace. `end_trace()` waits for any queued events in that workflow to finish delivery, then finalizes the trace by aggregating:

- step count
- total latency
- total cost
- total tokens
- overall success status
- step-level metadata

Example:

```python
from ai_guardian import start_trace, log_event, end_trace

trace_id = start_trace(session_id="rag-session", user_id="user-123")

log_event(
    trace_id,
    step_name="retrieval",
    input_prompt="Find relevant documents",
    output="3 documents retrieved",
    model_name="vector-search",
    latency_ms=42,
)

log_event(
    trace_id,
    step_name="generation",
    input_prompt="Answer using retrieved context",
    output="Generated answer",
    model_name="gpt-4o-mini",
    prompt_tokens=320,
    completion_tokens=110,
    latency_ms=850,
)

end_trace(trace_id)
```

---

## Python SDK

### Decorator-Based Tracking

```python
from ai_guardian import track_llm_call

@track_llm_call(
    model_name="gpt-4o-mini",
    session_id="user-123"
)
def call_llm(prompt):
    return openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
```

For OpenAI-style responses, the decorator attempts to extract:

- prompt tokens
- completion tokens
- total tokens
- output text
- finish reason

If the wrapped function raises an exception, AI Guardian records a failed event and re-raises the original exception so application behavior is preserved.

### LangChain Integration Example

The repository also includes a LangChain callback example that records LLM start/end/error events through the same SDK client.

---

## Dashboard

The React dashboard contains four main views.

### Dashboard Overview

Displays:

- total requests
- success rate
- average latency
- total estimated cost
- total tokens
- active alerts
- latency trend
- cost by model

### Events

Displays recent LLM interaction events and request metadata.

### Alerts

Displays active threshold violations and allows alerts to be resolved.

### Traces

Displays persisted multi-step workflow traces and their aggregate metrics.

Dashboard data refreshes every **10 seconds** through REST API polling.

---

## Project Structure

```text
ai-guardian/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routes/
│   │   │   ├── events.py
│   │   │   ├── metrics.py
│   │   │   ├── alerts.py
│   │   │   └── traces.py
│   │   └── services/
│   │       ├── cost_service.py
│   │       ├── evaluation_service.py
│   │       └── alert_service.py
│   └── tests/
│       └── test_tracker.py
│
├── sdk/
│   ├── ai_guardian/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── tracker.py
│   │   ├── models.py
│   │   └── utils.py
│   ├── examples/
│   │   ├── openai_tracked.py
│   │   └── langchain_tracked.py
│   ├── tests/
│   │   └── test_sdk_tracker.py
│   └── setup.py
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx
        └── pages/
            ├── Dashboard.jsx
            ├── EventsPage.jsx
            ├── AlertsPage.jsx
            └── TracesPage.jsx
```

---

## Quickstart

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 15+

### 1. Create the Database

The default local connection is:

```text
postgresql://postgres:password@localhost:5432/ai_guardian
```

Create the database:

```bash
createdb ai_guardian
```

For a different connection, set:

```bash
export DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DATABASE"
```

### 2. Start the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard:

```text
http://localhost:5173
```

### 4. Install the SDK

```bash
cd sdk
pip install -e .
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/events/` | Store a new LLM interaction event |
| `GET` | `/api/events/` | List events with filters |
| `GET` | `/api/events/{event_id}` | Retrieve one event |
| `GET` | `/api/metrics/summary` | Aggregate request metrics |
| `GET` | `/api/metrics/cost-by-model` | Aggregate cost by model |
| `GET` | `/api/metrics/latency-trend` | Recent latency measurements |
| `GET` | `/api/metrics/errors` | Recent failed requests |
| `GET` | `/api/alerts/` | List alerts |
| `PATCH` | `/api/alerts/{alert_id}/resolve` | Resolve an alert |
| `POST` | `/api/traces/` | Create a persistent workflow trace |
| `GET` | `/api/traces/` | List traces |
| `GET` | `/api/traces/{trace_id}` | Retrieve a trace and its events |
| `PATCH` | `/api/traces/{trace_id}/complete` | Aggregate and finalize a trace |

---

## Testing Event Ingestion

```bash
curl -X POST http://127.0.0.1:8000/api/events/ \
  -H "Content-Type: application/json" \
  -d '{
    "input_prompt": "What is machine learning?",
    "model_name": "gpt-4o-mini",
    "output": "Machine learning is a subset of artificial intelligence...",
    "prompt_tokens": 15,
    "completion_tokens": 20,
    "latency_ms": 1200,
    "success": true
  }'
```

The backend will:

```text
Receive Event
     ↓
Derive Total Tokens
     ↓
Estimate Cost
     ↓
Compute Heuristic Signals
     ↓
Persist Event
     ↓
Check Alert Thresholds
```

---

## Engineering Design Decisions

### Why FastAPI?

FastAPI provides request validation, automatic OpenAPI documentation, and a clean API layer for event ingestion and metrics retrieval.

### Why PostgreSQL?

Observability data is structured and frequently aggregated. A relational database makes it straightforward to query cost, latency, failures, alerts, and events associated with a trace.

### Why a Separate SDK?

The SDK decouples application instrumentation from monitoring infrastructure. AI applications emit structured telemetry without embedding database or analytics logic into the application itself.

### Why Background Event Delivery?

Observability should not noticeably increase the latency of the model call being measured. Event telemetry is therefore queued on a background thread pool while application execution continues.

### Why Lightweight Heuristics?

The current evaluation layer is inexpensive, deterministic, and does not require additional LLM API calls. It serves as an experimental baseline for more sophisticated evaluators.

---

## Configuration & Security Notes

### CORS

By default, the backend allows the local Vite development origins:

```text
http://localhost:5173
http://127.0.0.1:5173
```

Additional origins can be configured with:

```bash
export CORS_ORIGINS="https://example.com,https://admin.example.com"
```

### Prompt and Response Data

Prompts and outputs may contain sensitive information. A production deployment should add:

- authentication and authorization
- API keys
- configurable redaction
- retention policies
- encryption and access controls
- tenant isolation

---

## Current Limitations

AI Guardian is an engineering prototype rather than a production observability service.

### Heuristic Evaluation

Quality, groundedness, and hallucination-risk values are rule-based diagnostic indicators and do not establish factual correctness.

### In-Memory SDK Delivery Queue

Background telemetry uses an in-process thread pool. Events that have not been delivered may be lost if the host process terminates abruptly. A production implementation would use a durable queue or collector.

### Pricing Maintenance

Cost estimation depends on the configured pricing table and may become outdated as providers change prices.

### Polling-Based Dashboard Refresh

The dashboard currently refreshes every 10 seconds. WebSockets or Server-Sent Events would provide lower-latency streaming updates.

### Authentication and Multi-Tenancy

Authentication, API keys, role-based access control, and tenant isolation are not yet implemented.

---

## Roadmap

- [x] Structured LLM event ingestion
- [x] PostgreSQL persistence
- [x] Cost aggregation
- [x] Threshold-based alerts
- [x] Background SDK event delivery
- [x] Persistent trace lifecycle and aggregation
- [x] Polling-based dashboard refresh
- [ ] Durable telemetry queue / collector
- [ ] LLM-as-judge evaluation
- [ ] RAG source-grounded factuality checks
- [ ] Prompt regression testing
- [ ] Model A/B comparison dashboard
- [ ] Cost budgets and forecasting
- [ ] WebSocket or Server-Sent Event streaming
- [ ] Authentication and API keys
- [ ] Multi-tenant authorization
- [ ] Prompt and response redaction
- [ ] Slack / email integrations
- [ ] Docker Compose development environment
- [ ] Broader automated integration tests
- [ ] GitHub Actions CI pipeline

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI, Python |
| Database | PostgreSQL, SQLAlchemy |
| Validation | Pydantic |
| Frontend | React, Vite |
| Visualization | Recharts |
| SDK | Python, httpx |
| LLM Examples | OpenAI, LangChain |
| API Server | Uvicorn |

---

## Author

**Siham Boumalak**  
M.S. Artificial Intelligence — Machine Learning Concentration  
Khoury College of Computer Sciences, Northeastern University

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat-square&logo=linkedin)](https://linkedin.com/in/siham-boumalak-11014b210)
[![GitHub](https://img.shields.io/badge/GitHub-boumalaksiham-181717?style=flat-square&logo=github)](https://github.com/boumalaksiham)

---

## Project Status

AI Guardian is an active engineering prototype exploring **LLM observability, cost intelligence, application telemetry, workflow tracing, operational alerting, and AI-system evaluation**.
