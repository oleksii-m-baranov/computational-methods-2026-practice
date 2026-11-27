import unittest

from dispatcher import call_tool


class TestDispatcher(unittest.TestCase):

    def test_broken_json(self):
        level, _ = call_tool("product_info", '{"product":')
        self.assertEqual(level, "syntax")

    def test_wrong_type(self):
        level, _ = call_tool("product_info", '{"product": 123}')
        self.assertEqual(level, "schema")

    def test_missing_field(self):
        level, _ = call_tool("scale_amount", '{"amount": 300}')
        self.assertEqual(level, "schema")

    def test_extra_field(self):
        level, _ = call_tool(
            "product_info",
            '{"product": "рис", "extra": "value"}'
        )
        self.assertEqual(level, "schema")

    def test_unknown_tool(self):
        level, _ = call_tool("unknown_tool", '{}')
        self.assertEqual(level, "name")

    def test_forbidden_action(self):
        level, _ = call_tool("place_order", '{"item": "плов"}')
        self.assertEqual(level, "permission")

    def test_unknown_product(self):
        level, _ = call_tool("product_info", '{"product": "тунець"}')
        self.assertEqual(level, "meaning")

    def test_out_of_range_value(self):
        level, _ = call_tool(
            "scale_amount",
            '{"amount": 300, "base_servings": 0, "target_servings": 10}'
        )
        self.assertEqual(level, "schema")


if __name__ == "__main__":
    unittest.main(verbosity=2)
