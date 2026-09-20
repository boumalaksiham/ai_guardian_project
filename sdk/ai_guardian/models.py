from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class LLMEvent:
    input_prompt: str
    model_name: str
    output: Optional[str] = None
    trace_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    latency_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        return {
            "input_prompt": self.input_prompt, "model_name": self.model_name,
            "output": self.output, "trace_id": self.trace_id,
            "session_id": self.session_id, "user_id": self.user_id,
            "latency_ms": self.latency_ms, "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens, "total_tokens": self.total_tokens,
            "cost_usd": self.cost_usd, "success": self.success,
            "error_message": self.error_message, "tags": self.tags,
        }