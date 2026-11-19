import json
import config
from agent import run_agent, tool_cache

config.USE_CACHE = True
config.COMPRESS = True
config.USE_STATE = True

with open("long_task.json", encoding="utf-8") as file:
    task = json.load(file)

tool_cache.data.clear()
tool_cache.hits = 0
tool_cache.misses = 0

for repeat in range(1, 3):
    print(f"\nЗАПУСК {repeat}")

    answer = run_agent(
        task["question"],
        max_steps=config.MAX_STEPS_LONG
    )

    correct = (
        answer is not None
        and f"{task['expected']['total_monthly_payment']:.2f}" in answer
    )

    print("Правильний результат:", correct)
    print("Статистика кешу:", tool_cache.stats())

    assert correct

assert tool_cache.hits >= 18

print("\nLONG CACHE TEST: PASS")
