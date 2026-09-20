MODEL_COSTS = {
    "gpt-4o": {"prompt": 0.005, "completion": 0.015},
    "gpt-4o-mini": {"prompt": 0.00015, "completion": 0.0006},
    "gpt-4-turbo": {"prompt": 0.01, "completion": 0.03},
    "gpt-4": {"prompt": 0.03, "completion": 0.06},
    "gpt-3.5-turbo": {"prompt": 0.0005, "completion": 0.0015},
    "claude-3-opus": {"prompt": 0.015, "completion": 0.075},
    "claude-3-sonnet": {"prompt": 0.003, "completion": 0.015},
    "claude-3-haiku": {"prompt": 0.00025, "completion": 0.00125},
    "default": {"prompt": 0.001, "completion": 0.002},
}

def compute_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    model_key = "default"
    for key in MODEL_COSTS:
        if key in model_name.lower():
            model_key = key
            break
    rates = MODEL_COSTS[model_key]
    cost = (prompt_tokens / 1000 * rates["prompt"]) + (completion_tokens / 1000 * rates["completion"])
    return round(cost, 8)