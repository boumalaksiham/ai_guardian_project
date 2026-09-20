from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.db import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class LLMEvent(Base):
    __tablename__ = "llm_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    trace_id = Column(String, index=True, nullable=True)
    session_id = Column(String, index=True, nullable=True)
    user_id = Column(String, nullable=True)
    input_prompt = Column(Text, nullable=False)
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=True)
    temperature = Column(Float, nullable=True)
    max_tokens = Column(Integer, nullable=True)
    output = Column(Text, nullable=True)
    finish_reason = Column(String, nullable=True)
    latency_ms = Column(Float, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    quality_score = Column(Float, nullable=True)
    hallucination_risk = Column(Float, nullable=True)
    groundedness_score = Column(Float, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=generate_uuid)
    event_id = Column(String, nullable=True)
    alert_type = Column(String, nullable=False)
    severity = Column(String, default="warning")
    message = Column(Text, nullable=False)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Trace(Base):
    __tablename__ = "traces"

    id = Column(String, primary_key=True, default=generate_uuid)
    trace_id = Column(String, unique=True, index=True)
    session_id = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    total_latency_ms = Column(Float, nullable=True)
    total_cost_usd = Column(Float, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    step_count = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    steps = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
