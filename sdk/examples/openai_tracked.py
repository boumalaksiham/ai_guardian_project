import os, time
from openai import OpenAI
from ai_guardian import track_llm_call, start_trace, log_event, end_trace

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@track_llm_call(model_name="gpt-4o-mini", session_id="demo-session")
def ask(prompt: str):
    return openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

def rag_pipeline(user_query: str):
    trace_id = start_trace(session_id="rag-demo", user_id="user-001")

    t0 = time.time()
    retrieved_docs = ["Doc A: Return policy...", "Doc B: Electronics policy..."]
    log_event(trace_id, step_name="retrieval", input_prompt=user_query,
              output=str(retrieved_docs), model_name="vector-search",
              latency_ms=round((time.time() - t0) * 1000, 2))

    prompt = f"Context:\n{chr(10).join(retrieved_docs)}\n\nQuestion: {user_query}"
    t1 = time.time()
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
    answer = response.choices[0].message.content

    log_event(trace_id, step_name="generation", input_prompt=prompt, output=answer,
              model_name="gpt-4o-mini", prompt_tokens=response.usage.prompt_tokens,
              completion_tokens=response.usage.completion_tokens,
              latency_ms=round((time.time() - t1) * 1000, 2))

    end_trace(trace_id)
    return answer

if __name__ == "__main__":
    result = ask("What is observability in AI systems?")
    print(result.choices[0].message.content)