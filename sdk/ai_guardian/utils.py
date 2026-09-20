import time
from typing import Optional

def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def format_latency(ms: float) -> str:
    return f"{ms:.0f}ms" if ms < 1000 else f"{ms / 1000:.2f}s"

def safe_truncate(text: str, max_chars: int = 500) -> str:
    return text if len(text) <= max_chars else text[:max_chars] + "...[truncated]"

class Timer:
    def __enter__(self):
        self._start = time.time()
        return self
    def __exit__(self, *args):
        self.elapsed_ms = round((time.time() - self._start) * 1000, 2)