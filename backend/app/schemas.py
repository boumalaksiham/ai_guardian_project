from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class LLMEventCreate(BaseModel):
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    input_prompt: str
    model_name: str
    model_version: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    output: Optional[str] = None
    finish_reason: Optional[str] = None
    latency_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None

class LLMEventResponse(LLMEventCreate):
    id: str
    quality_score: Optional[float] = None
    hallucination_risk: Optional[float] = None
    groundedness_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AlertResponse(BaseModel):
    id: str
    event_id: Optional[str]
    alert_type: str
    severity: str
    message: str
    resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TraceCreate(BaseModel):
    trace_id: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None

class TraceResponse(TraceCreate):
    id: str
    total_latency_ms: Optional[float]
    total_cost_usd: Optional[float]
    total_tokens: Optional[int]
    step_count: int
    success: bool
    created_at: datetime

    class Config:
        from_attributes = True

class MetricsSummary(BaseModel):
    total_requests: int
    success_rate: float
    avg_latency_ms: float
    total_cost_usd: float
    total_tokens: int
    avg_quality_score: Optional[float]
    active_alerts: int
