"""Перевірка інструментів, описів і диспетчера без моделі."""
import tools
from tools import TOOLS
from schemas import SCHEMAS
from dispatcher import call_tool

print(tools.search_exercises("спина"))
print(tools.schedule_info("йога"))
print(tools.calc_calories(45, 70, 5))

print(len(SCHEMAS))
print({s["function"]["name"] for s in SCHEMAS} == set(TOOLS))

print(call_tool("search_exercises", '{"query": "спина"}'))
print(call_tool("delete_all", '{}'))
print(call_tool("search_exercises", '{"query": спина}'))
print(call_tool("search_exercises", '{"text": "спина"}'))
