from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import Trace, LLMEvent
from app.schemas import TraceCreate, TraceResponse

router = APIRouter()


@router.post("/", response_model=TraceResponse, status_code=status.HTTP_201_CREATED)
def create_trace(trace: TraceCreate, db: Session = Depends(get_db)):
    existing = db.query(Trace).filter(Trace.trace_id == trace.trace_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Trace already exists")

    db_trace = Trace(
        trace_id=trace.trace_id,
        session_id=trace.session_id,
        user_id=trace.user_id,
        steps=trace.steps or [],
        step_count=len(trace.steps or []),
        total_latency_ms=0.0,
        total_cost_usd=0.0,
        total_tokens=0,
        success=True,
    )
    db.add(db_trace)
    db.commit()
    db.refresh(db_trace)
    return db_trace


@router.get("/", response_model=List[TraceResponse])
def list_traces(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Trace).order_by(Trace.created_at.desc()).offset(skip).limit(limit).all()


@router.patch("/{trace_id}/complete", response_model=TraceResponse)
def complete_trace(trace_id: str, db: Session = Depends(get_db)):
    trace = db.query(Trace).filter(Trace.trace_id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    events = (
        db.query(LLMEvent)
        .filter(LLMEvent.trace_id == trace_id)
        .order_by(LLMEvent.created_at.asc())
        .all()
    )

    trace.step_count = len(events)
    trace.total_latency_ms = round(sum(e.latency_ms or 0 for e in events), 2)
    trace.total_cost_usd = round(sum(e.cost_usd or 0 for e in events), 8)
    trace.total_tokens = sum(e.total_tokens or 0 for e in events)
    trace.success = all(e.success for e in events) if events else True
    trace.steps = [
        {
            "event_id": e.id,
            "step": (e.tags or {}).get("step"),
            "model_name": e.model_name,
            "latency_ms": e.latency_ms,
            "cost_usd": e.cost_usd,
            "success": e.success,
        }
        for e in events
    ]

    db.commit()
    db.refresh(trace)
    return trace


@router.get("/{trace_id}")
def get_trace(trace_id: str, db: Session = Depends(get_db)):
    trace = db.query(Trace).filter(Trace.trace_id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    events = (
        db.query(LLMEvent)
        .filter(LLMEvent.trace_id == trace_id)
        .order_by(LLMEvent.created_at.asc())
        .all()
    )
    return {"trace": trace, "events": events}
