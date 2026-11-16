import json
from pathlib import Path
from langfuse import get_client, propagate_attributes
from dispatcher import call_tool

cases = [
    ("broken_json", "product_info", '{"product": "рис"', "syntax"),
    ("wrong_type", "scale_amount", '{"amount":"сто","base_servings":4,"target_servings":10}', "schema"),
    ("missing_field", "product_info", '{}', "schema"),
    ("extra_field", "product_info", '{"product":"рис","x":1}', "schema"),
    ("unknown_tool", "delete_all", '{}', "name"),
    ("forbidden_action", "place_order", '{"product":"рис"}', "permission"),
    ("missing_product", "product_info", '{"product":"лимон"}', "meaning"),
    ("out_of_bounds", "scale_amount", '{"amount":300,"base_servings":0,"target_servings":10}', "schema"),
    ("valid_scale", "scale_amount", '{"amount":300,"base_servings":4,"target_servings":10}', "ok"),
]
output = Path("test_checks_results.json")
if output.exists():
    raise SystemExit("TEST_RESULTS_EXIST. Do not overwrite results.")
records = []
try:
    with propagate_attributes(trace_name="dispatcher-tests", tags=["tests"]):
        for label, name, raw, expected in cases:
            level, message = call_tool(name, raw)
            records.append({"case": label, "name": name, "arguments": raw, "level": level, "message": message, "expected_level": expected, "passed": level == expected})
            print(f"{label}: {level} / expected={expected} / {'PASS' if level == expected else 'FAIL'}", flush=True)
finally:
    output.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    get_client().flush()
if not all(r["passed"] for r in records):
    raise SystemExit("TEST_FAILED. Do not run agent_runner.py.")
print("ALL_TESTS_PASSED")
