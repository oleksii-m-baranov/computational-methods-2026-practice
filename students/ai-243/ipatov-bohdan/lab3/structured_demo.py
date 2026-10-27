"""Structured output demo using Ollama json_schema (Extra Task). Variant 11 (Library)."""
import json
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calculate"].model_json_schema()

test_queries = [
    (
        "1. Стандартний запит",
        "Я затримав книжку на 5 днів, штраф становить 10 грн за день. Сформуй аргументи для розрахунку штрафу.",
    ),
    (
        "2. Числа словами",
        "Затримка сім днів, ставка штрафу п'ятнадцять гривень на добу. Сформуй аргументи для калькулятора.",
    ),
    (
        "3. Значення поза межами (від'ємні дні -10) або заборонена дія (ділення div)",
        "Поділи сто на п'ять. Сформуй аргументи для калькулятора.",
    ),
]

print("=" * 70)
print("ДЕМОНСТРАЦІЯ STRUCTURED OUTPUT (СЕРВЕРНА ГРАМАТИЧНА ВАЛІДАЦІЯ)")
print("=" * 70)

for title, query in test_queries:
    print(f"\n>>> {title}")
    print(f"Запит: {query}")
    try:
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=[{"role": "user", "content": query}],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "calculate_args", "schema": schema},
            },
            temperature=0,
        )
        text = response.choices[0].message.content
        print(f"Сира відповідь: {text}")
        validated = ARGS["calculate"].model_validate_json(text)
        print(f"Pydantic валідація: УСПІШНО -> {validated}")
    except Exception as e:
        print(f"Помилка: {e}")
