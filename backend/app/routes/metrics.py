from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
from app.models import LLMEvent, Alert
from app.schemas import MetricsSummary

router = APIRouter()

@router.get("/summary", response_model=MetricsSummary)
def get_summary(db: Session = Depends(get_db)):
    total = db.query(LLMEvent).count()
    success_count = db.query(LLMEvent).filter(LLMEvent.success == True).count()
    avg_latency = db.query(func.avg(LLMEvent.latency_ms)).scalar() or 0.0
    total_cost = db.query(func.sum(LLMEvent.cost_usd)).scalar() or 0.0
    total_tokens = db.query(func.sum(LLMEvent.total_tokens)).scalar() or 0
    avg_quality = db.query(func.avg(LLMEvent.quality_score)).scalar()
    active_alerts = db.query(Alert).filter(Alert.resolved == False).count()

    return MetricsSummary(
        total_requests=total,
        success_rate=round((success_count / total * 100) if total > 0 else 0, 2),
        avg_latency_ms=round(avg_latency, 2),
        total_cost_usd=round(total_cost, 6),
        total_tokens=total_tokens,
        avg_quality_score=round(avg_quality, 2) if avg_quality else None,
        active_alerts=active_alerts,
    )

@router.get("/cost-by-model")
def cost_by_model(db: Session = Depends(get_db)):
    results = (
        db.query(LLMEvent.model_name, func.sum(LLMEvent.cost_usd), func.count(LLMEvent.id))
        .group_by(LLMEvent.model_name)
        .all()
    )
    return [
        {"model": r[0], "total_cost_usd": round(r[1] or 0, 6), "request_count": r[2]}
        for r in results
    ]

@router.get("/latency-trend")
def latency_trend(db: Session = Depends(get_db)):
    events = (
        db.query(LLMEvent.created_at, LLMEvent.latency_ms)
        .filter(LLMEvent.latency_ms != None)
        .order_by(LLMEvent.created_at.desc())
        .limit(100)
        .all()
    )
    return [{"timestamp": str(e[0]), "latency_ms": e[1]} for e in events]

@router.get("/errors")
def error_events(db: Session = Depends(get_db)):
    events = (
        db.query(LLMEvent)
        .filter(LLMEvent.success == False)
        .order_by(LLMEvent.created_at.desc())
        .limit(50)
        .all()
    )
    return [{"id": e.id, "model": e.model_name, "error": e.error_message, "time": str(e.created_at)} for e in events]