from typing import Optional, Dict, Any

def evaluate_output(input_prompt: Optional[str], output: Optional[str]) -> Dict[str, Any]:
    if not output:
        return {"quality_score": None, "hallucination_risk": None, "groundedness_score": None}
    return {
        "quality_score": _score_quality(input_prompt, output),
        "hallucination_risk": _estimate_hallucination_risk(output),
        "groundedness_score": _estimate_groundedness(output),
    }

def _score_quality(prompt, output):
    score = 0.5
    words = len(output.split())
    if 20 <= words <= 500:
        score += 0.2
    elif words < 5:
        score -= 0.3
    refusal_phrases = ["i cannot", "i'm sorry", "i am unable", "as an ai"]
    if any(p in output.lower() for p in refusal_phrases):
        score -= 0.1
    return round(min(max(score, 0.0), 1.0), 2)

def _estimate_hallucination_risk(output):
    risk = 0.2
    high_risk = ["definitely", "absolutely", "100%", "certainly", "guaranteed", "always", "never"]
    for p in high_risk:
        if p in output.lower():
            risk += 0.1
    return round(min(risk, 1.0), 2)

def _estimate_groundedness(output):
    score = 0.5
    grounding = ["according to", "based on", "the document states", "as mentioned"]
    for p in grounding:
        if p in output.lower():
            score += 0.1
    return round(min(score, 1.0), 2)