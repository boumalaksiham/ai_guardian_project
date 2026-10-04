import re


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
    """Use an exact configured name or a dated snapshot, never a substring.

    Rates are USD per 1,000 tokens. Unknown names retain the diagnostic
    default rate; this function does not fetch current provider pricing.
    """
    name = model_name.strip().lower()
    model_key = name if name in MODEL_COSTS else "default"
    if model_key == "default":
        for key in sorted(MODEL_COSTS, key=len, reverse=True):
            suffix = name.removeprefix(key + "-")
            if name.startswith(key + "-") and re.fullmatch(r"(?:\d{4}-\d{2}-\d{2}|\d{8}|\d{4})", suffix):
                model_key = key
                break
    rates = MODEL_COSTS[model_key]
    cost = (prompt_tokens / 1000 * rates["prompt"]) + (completion_tokens / 1000 * rates["completion"])
    return round(cost, 8)
