"""Перевірки без моделі (кроки 2-4 методички)."""
import tools
from schemas import SCHEMAS
from dispatcher import call_tool

print(tools.search_rules("скло"))
print(tools.tariff_info("Львів"))
print(tools.tariff_info("Мадрид"))
print(tools.calc_price(15, 18, 70))
print(tools.calc_price(1, 18, 70))

print(len(SCHEMAS))
print({s["function"]["name"] for s in SCHEMAS} == set(tools.TOOLS))

print(call_tool("search_rules", '{"query": "скло"}'))
print(call_tool("delete_all", '{}'))
print(call_tool("search_rules", '{"query": скло}'))
print(call_tool("search_rules", '{"text": "скло"}'))
