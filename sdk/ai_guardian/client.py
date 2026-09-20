import atexit
import os
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Optional, Dict, Any

import httpx


class GuardianClient:
    """HTTP client for AI Guardian.

    Event telemetry is delivered on a small background thread pool so a slow or
    unavailable observability backend does not block the host LLM application.
    Trace finalization waits only for pending events belonging to that trace so
    aggregate trace metrics are computed from the complete workflow.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 5, max_workers: int = 2):
        self.base_url = (base_url or os.getenv("AI_GUARDIAN_URL", "http://localhost:8000")).rstrip("/")
        self.timeout = timeout
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="ai-guardian")
        self._pending_by_trace: Dict[str, list[Future]] = {}
        self._pending_lock = threading.Lock()
        self._closed = False
        atexit.register(self.close)

    def _request(self, method: str, path: str, **kwargs) -> Optional[Dict]:
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, f"{self.base_url}{path}", **kwargs)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[AI Guardian] Warning: {method} {path} failed — {e}")
            return None

    def send_event(self, event_data: Dict[str, Any]) -> Future:
        """Queue an event for best-effort background delivery."""
        if self._closed:
            raise RuntimeError("GuardianClient is closed")

        future = self._executor.submit(self._request, "POST", "/api/events/", json=event_data)
        trace_id = event_data.get("trace_id")
        if trace_id:
            with self._pending_lock:
                self._pending_by_trace.setdefault(trace_id, []).append(future)
        return future

    def create_trace(self, trace_data: Dict[str, Any]) -> Optional[Dict]:
        return self._request("POST", "/api/traces/", json=trace_data)

    def complete_trace(self, trace_id: str) -> Optional[Dict]:
        # Ensure all queued events for this workflow have reached the backend
        # before the backend computes aggregate trace metrics.
        with self._pending_lock:
            pending = self._pending_by_trace.pop(trace_id, [])
        for future in pending:
            try:
                future.result(timeout=self.timeout + 1)
            except Exception as e:
                print(f"[AI Guardian] Warning: trace event delivery failed — {e}")

        return self._request("PATCH", f"/api/traces/{trace_id}/complete")

    def get_summary(self) -> Optional[Dict]:
        return self._request("GET", "/api/metrics/summary")

    def close(self):
        if not self._closed:
            self._closed = True
            self._executor.shutdown(wait=True, cancel_futures=False)
