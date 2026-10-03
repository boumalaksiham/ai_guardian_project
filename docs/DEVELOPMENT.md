# Development and testing

Follow the root README to start PostgreSQL, the API, and the dashboard. Database settings must be exported into the same shell that starts Uvicorn. A startup connection error usually means the database service, database name, or credentials are incorrect.

## API smoke check

```bash
curl http://localhost:8000/health
```

A healthy response confirms the API process responds. It does not verify every ingestion, aggregation, or dashboard path. Use `/docs` to inspect the actual request schemas and submit synthetic, non-sensitive events when testing ingestion.

## Unit tests

From the repository root in an activated Python environment:

```bash
python -m pip install pytest httpx==0.27.0 pydantic==2.6.4
PYTHONPATH=backend:sdk python -m pytest backend/tests sdk/tests
```

In PowerShell set `$env:PYTHONPATH = "backend;sdk"` before running pytest. The GitHub Actions workflow uses Python 3.12. These tests cover SDK delivery and selected service behavior with test doubles; they do not constitute an end-to-end PostgreSQL or browser test.

## Frontend build

```bash
cd frontend
npm ci
npm run build
```

This checks compilation. It does not establish that live dashboard data or every interaction works.

## Interpretation and deployment

Quality signals are heuristics, rather than validated measures of factuality. Cost estimates depend on the maintained pricing table and recorded token counts. Review unknown-model behavior before using totals for budgeting. The SDK queue is in memory, so process termination can lose pending telemetry.

For shared deployment, implement authentication, authorization, retention, and prompt redaction; configure database credentials, CORS, and frontend API addresses for the environment. Development defaults are not a production deployment configuration.
