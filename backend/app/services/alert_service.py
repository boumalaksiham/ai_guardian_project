import os
import uuid

from sqlalchemy.orm import Session

from app.models import Alert, LLMEvent

LATENCY_THRESHOLD_MS = float(os.getenv("ALERT_LATENCY_MS", "5000"))
COST_THRESHOLD_USD = float(os.getenv("ALERT_COST_USD", "0.10"))
QUALITY_THRESHOLD = float(os.getenv("ALERT_QUALITY_MIN", "0.4"))
HALLUCINATION_THRESHOLD = float(os.getenv("ALERT_HALLUCINATION_RISK", "0.7"))


def check_and_create_alerts(db: Session, event: LLMEvent):
    alerts = []

    if event.latency_ms is not None and event.latency_ms > LATENCY_THRESHOLD_MS:
        alerts.append(Alert(
            id=str(uuid.uuid4()),
            event_id=event.id,
            alert_type="latency",
            severity="warning",
            message=f"High latency: {event.latency_ms:.0f}ms on {event.model_name}",
        ))

    if event.cost_usd is not None and event.cost_usd > COST_THRESHOLD_USD:
        alerts.append(Alert(
            id=str(uuid.uuid4()),
            event_id=event.id,
            alert_type="cost",
            severity="warning",
            message=f"High cost: ${event.cost_usd:.4f} on {event.model_name}",
        ))

    if event.quality_score is not None and event.quality_score < QUALITY_THRESHOLD:
        alerts.append(Alert(
            id=str(uuid.uuid4()),
            event_id=event.id,
            alert_type="quality",
            severity="warning",
            message=f"Low quality score: {event.quality_score} on {event.model_name}",
        ))

    if event.hallucination_risk is not None and event.hallucination_risk > HALLUCINATION_THRESHOLD:
        alerts.append(Alert(
            id=str(uuid.uuid4()),
            event_id=event.id,
            alert_type="hallucination_risk",
            severity="critical",
            message=f"High heuristic hallucination-risk score: {event.hallucination_risk} on {event.model_name}",
        ))

    if not event.success:
        alerts.append(Alert(
            id=str(uuid.uuid4()),
            event_id=event.id,
            alert_type="error",
            severity="critical",
            message=f"Request failed on {event.model_name}: {event.error_message or 'Unknown error'}",
        ))

    for alert in alerts:
        db.add(alert)
    if alerts:
        db.commit()
