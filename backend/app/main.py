import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import engine, Base
from app.routes import events, metrics, alerts, traces

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Guardian",
    description="LLM Observability & Cost Intelligence Platform",
    version="1.1.0",
)

cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(traces.router, prefix="/api/traces", tags=["Traces"])


@app.get("/")
def root():
    return {"status": "AI Guardian is running", "version": "1.1.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}
