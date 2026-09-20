import functools
import time
import uuid
from typing import Optional, Callable, Dict

from ai_guardian.client import GuardianClient

_default_client = GuardianClient()
_active_traces: Dict[str, Dict] = {}


def track_llm_call(model_name="unknown", session_id=None, user_id=None, trace_id=None, client=None):
    _client = client or _default_client

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            event_data = {
                "model_name": model_name,
                "session_id": session_id,
                "user_id": user_id,
                "trace_id": trace_id or str(uuid.uuid4()),
                "input_prompt": str(args[0]) if args else str(kwargs.get("prompt", "")),
                "success": True,
            }
            start = time.time()
            try:
                result = func(*args, **kwargs)
                event_data["latency_ms"] = round((time.time() - start) * 1000, 2)

                if hasattr(result, "usage") and result.usage:
                    event_data["prompt_tokens"] = getattr(result.usage, "prompt_tokens", None)
                    event_data["completion_tokens"] = getattr(result.usage, "completion_tokens", None)
                    event_data["total_tokens"] = getattr(result.usage, "total_tokens", None)

                if hasattr(result, "choices") and result.choices:
                    choice = result.choices[0]
                    message = getattr(choice, "message", None)
                    event_data["output"] = getattr(message, "content", None) if message else None
                    event_data["finish_reason"] = getattr(choice, "finish_reason", None)
                elif isinstance(result, str):
                    event_data["output"] = result

                _client.send_event(event_data)
                return result
            except Exception as e:
                event_data["latency_ms"] = round((time.time() - start) * 1000, 2)
                event_data["success"] = False
                event_data["error_message"] = str(e)
                _client.send_event(event_data)
                raise

        return wrapper

    return decorator


def start_trace(session_id=None, user_id=None, client=None) -> str:
    _client = client or _default_client
    trace_id = str(uuid.uuid4())
    _active_traces[trace_id] = {
        "trace_id": trace_id,
        "session_id": session_id,
        "user_id": user_id,
        "start_time": time.time(),
    }
    _client.create_trace({
        "trace_id": trace_id,
        "session_id": session_id,
        "user_id": user_id,
    })
    return trace_id


def log_event(
    trace_id,
    step_name,
    input_prompt,
    output=None,
    model_name="unknown",
    prompt_tokens=None,
    completion_tokens=None,
    latency_ms=None,
    success=True,
    error_message=None,
    client=None,
):
    _client = client or _default_client
    trace_info = _active_traces.get(trace_id, {})
    total_tokens = None
    if prompt_tokens is not None or completion_tokens is not None:
        total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

    return _client.send_event({
        "trace_id": trace_id,
        "session_id": trace_info.get("session_id"),
        "user_id": trace_info.get("user_id"),
        "input_prompt": input_prompt,
        "output": output,
        "model_name": model_name,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "latency_ms": latency_ms,
        "success": success,
        "error_message": error_message,
        "tags": {"step": step_name},
    })


def end_trace(trace_id: str, client=None):
    _client = client or _default_client
    result = _client.complete_trace(trace_id)
    _active_traces.pop(trace_id, None)
    return result
