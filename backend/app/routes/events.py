from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.models import LLMEvent
from app.schemas import LLMEventCreate, LLMEventResponse
from app.services.cost_service import compute_cost
from app.services.evaluation_service import evaluate_output
from app.services.alert_service import check_and_create_alerts
import uuid

router = APIRouter()

@router.post("/", response_model=LLMEventResponse)
def create_event(event: LLMEventCreate, db: Session = Depends(get_db)):
    event_dict = event.model_dump()

    if event_dict.get("total_tokens") is None and (
        event.prompt_tokens is not None or event.completion_tokens is not None
    ):
        event_dict["total_tokens"] = (event.prompt_tokens or 0) + (event.completion_tokens or 0)

    if event.cost_usd is None and (
        event.prompt_tokens is not None and event.completion_tokens is not None
    ):
        event_dict["cost_usd"] = compute_cost(
            event.model_name, event.prompt_tokens, event.completion_tokens
        )

    quality_scores = evaluate_output(event.input_prompt, event.output)
    event_dict.update(quality_scores)

    db_event = LLMEvent(id=str(uuid.uuid4()), **event_dict)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    check_and_create_alerts(db, db_event)
    return db_event

@router.get("/", response_model=List[LLMEventResponse])
def list_events(
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    model_name: Optional[str] = None,
    success: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(LLMEvent)
    if model_name:
        query = query.filter(LLMEvent.model_name == model_name)
    if success is not None:
        query = query.filter(LLMEvent.success == success)
    return query.order_by(LLMEvent.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{event_id}", response_model=LLMEventResponse)
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(LLMEvent).filter(LLMEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event