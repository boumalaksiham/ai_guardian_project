from app.services.cost_service import compute_cost
from app.services.evaluation_service import evaluate_output


def test_cost_computation():
    cost = compute_cost("gpt-4o-mini", 100, 200)
    assert cost > 0


def test_evaluation_service():
    result = evaluate_output("What is AI?", "AI stands for Artificial Intelligence.")
    assert "quality_score" in result
    assert "hallucination_risk" in result
    assert "groundedness_score" in result


def test_hallucination_signal_is_heuristic():
    ordinary = evaluate_output("", "This response may be correct.")["hallucination_risk"]
    confident = evaluate_output("", "This is absolutely guaranteed and always correct.")["hallucination_risk"]
    assert confident > ordinary
