import unittest
from app.services.cost_service import compute_cost


class CostLookupTests(unittest.TestCase):
    def test_mini_is_not_charged_at_full_model_rate(self):
        self.assertEqual(compute_cost("gpt-4o-mini", 1000, 1000), 0.00075)
        self.assertEqual(compute_cost("gpt-4o", 1000, 1000), 0.02)

    def test_case_whitespace_and_dated_snapshots(self):
        for name in (" GPT-4O-MINI ", "gpt-4o-mini-2024-07-18"):
            self.assertEqual(compute_cost(name, 1000, 1000), 0.00075)
        self.assertEqual(compute_cost("claude-3-haiku-20240307", 1000, 1000), 0.0015)
        self.assertEqual(compute_cost("gpt-4-0613", 1000, 1000), 0.09)

    def test_unknown_names_do_not_inherit_a_substring_rate(self):
        for name in ("custom-gpt-4o", "gpt-4o-miniature", "gpt-4o-mini-preview", ""):
            self.assertEqual(compute_cost(name, 1000, 1000), 0.003)

    def test_token_counts_and_zero_usage(self):
        self.assertEqual(compute_cost("gpt-4o-mini", 100, 200), 0.000135)
        self.assertEqual(compute_cost("gpt-4o-mini", 0, 0), 0.0)
