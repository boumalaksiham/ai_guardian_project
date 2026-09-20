from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models import Alert
from app.schemas import AlertResponse

router = APIRouter()


@router.get("/", response_model=List[AlertResponse])
def list_alerts(resolved: bool = False, db: Session = Depends(get_db)):
    return (
        db.query(Alert)
        .filter(Alert.resolved == resolved)
        .order_by(Alert.created_at.desc())
        .limit(100)
        .all()
    )


@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: str, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.resolved = True
    db.commit()
    return {"status": "resolved", "alert_id": alert_id}
