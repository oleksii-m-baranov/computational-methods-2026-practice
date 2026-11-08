"""Перевірка інструментів і описів без моделі (кроки 2-3)."""
import tools
from tools import TOOLS
from schemas import SCHEMAS

print(tools.search_routes("історія"))
print(tools.transport_info("Кам'янець-Подільський"))
print(tools.transport_info("Олеський замок"))
print(tools.calc_budget(420, 3, 500))

print(len(SCHEMAS))
print({s["function"]["name"] for s in SCHEMAS} == set(TOOLS))
