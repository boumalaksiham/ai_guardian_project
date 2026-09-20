from ai_guardian.tracker import start_trace, log_event, end_trace, track_llm_call


class FakeFuture:
    pass


class FakeClient:
    def __init__(self):
        self.events = []
        self.created = []
        self.completed = []

    def send_event(self, event):
        self.events.append(event)
        return FakeFuture()

    def create_trace(self, trace):
        self.created.append(trace)
        return trace

    def complete_trace(self, trace_id):
        self.completed.append(trace_id)
        return {"trace_id": trace_id}


def test_trace_lifecycle_and_event_metadata():
    client = FakeClient()
    trace_id = start_trace(session_id="session-1", user_id="user-1", client=client)
    log_event(
        trace_id,
        step_name="generation",
        input_prompt="hello",
        output="world",
        model_name="demo-model",
        prompt_tokens=3,
        completion_tokens=4,
        client=client,
    )
    end_trace(trace_id, client=client)

    assert client.created[0]["trace_id"] == trace_id
    assert client.events[0]["trace_id"] == trace_id
    assert client.events[0]["total_tokens"] == 7
    assert client.events[0]["tags"]["step"] == "generation"
    assert client.completed == [trace_id]


def test_decorator_records_successful_string_result():
    client = FakeClient()

    @track_llm_call(model_name="demo-model", client=client)
    def ask(prompt):
        return "answer"

    assert ask("question") == "answer"
    assert client.events[0]["input_prompt"] == "question"
    assert client.events[0]["output"] == "answer"
    assert client.events[0]["success"] is True
