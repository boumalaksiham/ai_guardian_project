# AI Guardian — LLM Observability & Cost Intelligence Platform

> A full-stack observability prototype for tracking LLM latency, token usage, estimated cost, failures, heuristic quality signals, alerts, and multi-step workflow traces.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)
![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite)

---

## What this project makes visible

An LLM application may produce an answer without showing which call was slow, how many tokens it used, or which workflow step failed. AI Guardian connects application instrumentation to stored events and a dashboard so those questions can be inspected at call and trace level.

The implemented deliverables are a **Python SDK, FastAPI ingestion and metrics API, PostgreSQL event/alert/trace storage, and React dashboard**. The dashboard polls the API every 10 seconds. It displays stored telemetry; it does not run or verify the monitored model itself.

**Start here:** [SDK tracker](sdk/ai_guardian/tracker.py), [event route](backend/app/routes/events.py), [database models](backend/app/models.py), and [dashboard](frontend/src/pages/Dashboard.jsx). [Development instructions](docs/DEVELOPMENT.md) cover verification and troubleshooting.

## Architecture

```mermaid
flowchart TD
    A[Instrumented Python application] --> B[Python SDK]
    B --> C[FastAPI backend]
    C --> D[PostgreSQL]
    E[React dashboard] -->|Polls metrics and records| C
```

The SDK separates instrumentation from storage and analysis. Its background delivery keeps telemetry requests off the wrapped call's foreground path, but introduces best-effort delivery and possible loss at process shutdown. Trace finalization waits for queued futures before requesting aggregation; failed deliveries still affect completeness.

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

The backend estimates request cost from prompt and completion token counts using the configured per-model pricing table (USD per 1,000 tokens).

Model lookup uses exact configured names and recognized dated snapshot suffixes. For example, `gpt-4o-mini` and `gpt-4o-mini-2024-07-18` use the mini rate; unrelated names containing `gpt-4o` do not. Unknown names use a default rate. Rates remain a static diagnostic configuration, not current provider billing. Regression tests cover mini/full-model distinctions, snapshot names, unknown-name boundaries, and token arithmetic.

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

`start_trace()` creates a persistent trace record. `log_event()` associates workflow steps with that trace. `end_trace()` waits on queued delivery futures for that trace (with per-future timeouts), then requests backend finalization. Failed or timed-out delivery can leave events absent from the aggregate. The backend aggregates:

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

The repository includes a LangChain callback example that records LLM start/end/error events through the SDK client. Install optional example dependencies from the repository root:

```bash
python -m pip install -e "./sdk[openai]"
# Or, for the LangChain example:
python -m pip install -e "./sdk[langchain]"
```

Provider examples require your own `OPENAI_API_KEY` and make billable model calls. The callback uses the generic model name `langchain-llm`, so the backend applies its default rate rather than the provider-specific rate. Optional dependency ranges are not locked; verify compatibility with the example imports before treating them as a reproducible integration.

---

## Dashboard views

| View | Question it helps answer |
|---|---|
| Overview | How many requests, failures, tokens, and estimated dollars are represented in the stored events? |
| Events | What prompt, response, model, latency, and status were recorded for an individual call? |
| Alerts | Which stored events crossed the configured thresholds, and which alerts remain unresolved? |
| Traces | Which steps belong to a workflow, and what are their aggregate metrics? |

## Quickstart

Use Python 3.12 (the CI environment), Node.js 18+, and a running PostgreSQL instance. Start backend and frontend in separate terminals. These examples assume a local development database.

```bash
git clone https://github.com/boumalaksiham/ai_guardian_project.git
cd ai_guardian_project
python -m venv .venv
source .venv/bin/activate
python -m pip install -r backend/requirements.txt
python -m pip install -e ./sdk
createdb ai_guardian
export DATABASE_URL="postgresql://postgres:password@localhost:5432/ai_guardian"
cd backend
uvicorn app.main:app --reload
```

Replace the connection string with your actual database credentials. On Windows use PowerShell activation and `$env:DATABASE_URL = "..."`. The backend reads environment variables directly; creating a `.env` file alone does not load them. PostgreSQL must be reachable before startup because table creation runs during application import.

The API is at `http://localhost:8000`, its interactive schema is at `http://localhost:8000/docs`, and its health endpoint is at `http://localhost:8000/health`.

In another terminal, starting from the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Open the address printed by Vite, normally `http://localhost:5173`. The frontend uses the local backend address. See [development and testing](docs/DEVELOPMENT.md) for checks and troubleshooting.

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

## Engineering decisions and tradeoffs

| Decision | Reason and practical limit |
|---|---|
| Separate SDK | Keeps database and analytics logic out of instrumented applications; response extraction still depends on the returned object format. |
| PostgreSQL | Supports structured records and aggregates; a reachable database is required during backend initialization. |
| Background delivery | Reduces foreground telemetry work; the in-memory queue is not durable. |
| Deterministic response heuristics | Avoids another model call for every event; language cues do not verify factual correctness. |
| REST polling | Gives a simple dashboard refresh path; updates are periodic rather than streamed. |

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

## Next engineering priorities

1. Maintain the pricing configuration and make unknown-model estimates explicit in the UI.
2. Add durable delivery and broader ingestion/trace integration tests.
3. Add authentication, authorization, redaction, and retention controls before a public deployment.
4. Evaluate source-grounded response checks against labeled examples before making factuality claims.

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

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/siham-boumalak/)
[![GitHub](https://img.shields.io/badge/GitHub-boumalaksiham-181717?style=flat-square&logo=github)](https://github.com/boumalaksiham)

---

## Project Status

AI Guardian is an active engineering prototype exploring **LLM observability, cost intelligence, application telemetry, workflow tracing, operational alerting, and AI-system evaluation**.
