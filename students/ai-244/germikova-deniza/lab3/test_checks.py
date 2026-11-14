
"""Тести перевірок викликів інструментів."""

import unittest

from dispatcher import call_tool


class TestChecks(unittest.TestCase):

    def test_broken_json(self):
        level, message = call_tool(
            "search_recipes",
            '{"query":'
        )

        self.assertEqual(level, "syntax")
        self.assertIn("JSON", message)

    def test_bad_type(self):
        level, message = call_tool(
            "scale_amount",
            '{"amount":"abc","base_servings":2,"target_servings":4}'
        )

        self.assertEqual(level, "schema")
        self.assertIn("amount", message)

    def test_missing_required(self):
        level, message = call_tool(
            "search_recipes",
            '{}'
        )

        self.assertEqual(level, "schema")
        self.assertIn("query", message)

    def test_extra_field(self):
        level, message = call_tool(
            "search_recipes",
            '{"query":"курка","unexpected":true}'
        )

        self.assertEqual(level, "schema")
        self.assertIn("unexpected", message)

    def test_unknown_tool(self):
        level, message = call_tool(
            "unknown_tool",
            '{}'
        )

        self.assertEqual(level, "name")
        self.assertIn("unknown_tool", message)

    def test_forbidden_action(self):
        level, message = call_tool(
            "place_order",
            '{"product":"рис"}'
        )

        self.assertEqual(level, "permission")
        self.assertIn("заборонено", message)

    def test_unknown_product(self):
        level, message = call_tool(
            "product_info",
            '{"product":"несуществующий продукт"}'
        )

        self.assertEqual(level, "meaning")
        self.assertIn("каталогу", message)

    def test_out_of_range(self):
        level, message = call_tool(
            "scale_amount",
            '{"amount":0,"base_servings":2,"target_servings":4}'
        )

        self.assertEqual(level, "schema")
        self.assertIn("amount", message)


if __name__ == "__main__":
    unittest.main(verbosity=2)
