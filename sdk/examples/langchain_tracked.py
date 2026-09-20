from langchain.callbacks.base import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from langchain.schema import LLMResult
from typing import Any, Dict, List, Optional, Union
import time, uuid
from ai_guardian.client import GuardianClient

class AIGuardianCallback(BaseCallbackHandler):
    def __init__(self, client=None, session_id=None):
        self.client = client or GuardianClient()
        self.session_id = session_id
        self._start_times = {}
        self._prompts = {}

    def on_llm_start(self, serialized, prompts, **kwargs):
        run_id = str(kwargs.get("run_id", uuid.uuid4()))
        self._start_times[run_id] = time.time()
        self._prompts[run_id] = prompts[0] if prompts else ""

    def on_llm_end(self, response: LLMResult, **kwargs):
        run_id = str(kwargs.get("run_id", ""))
        latency_ms = round((time.time() - self._start_times.pop(run_id, time.time())) * 1000, 2)
        prompt = self._prompts.pop(run_id, "")
        output = response.generations[0][0].text if response.generations else ""
        token_usage = response.llm_output.get("token_usage", {}) if response.llm_output else {}
        self.client.send_event({
            "input_prompt": prompt, "output": output,
            "model_name": "langchain-llm", "session_id": self.session_id,
            "latency_ms": latency_ms,
            "prompt_tokens": token_usage.get("prompt_tokens"),
            "completion_tokens": token_usage.get("completion_tokens"),
            "total_tokens": token_usage.get("total_tokens"),
            "success": True,
        })

    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs):
        run_id = str(kwargs.get("run_id", ""))
        prompt = self._prompts.pop(run_id, "")
        self.client.send_event({
            "input_prompt": prompt, "model_name": "langchain-llm",
            "session_id": self.session_id, "success": False, "error_message": str(error),
        })

if __name__ == "__main__":
    llm = ChatOpenAI(model="gpt-4o-mini", callbacks=[AIGuardianCallback(session_id="langchain-demo")])
    print(llm.invoke("Explain LLM observability in 2 sentences.").content)