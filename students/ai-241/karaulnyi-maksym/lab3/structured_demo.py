"""Демонстрація структурованого виводу (Structured Outputs) через Pydantic."""
import json
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["search_books"].model_json_schema()

print("=== Схема аргументів search_books ===")
print(json.dumps(schema, ensure_ascii=False, indent=2))

try:
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[
            {
                "role": "user",
                "content": "Знайди щось про алгоритми сортування. Сформуй валідні аргументи.",
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "args", "schema": schema},
        },
    )
    text = response.choices[0].message.content
    print("\n=== Відповідь сервера ===")
    print(text)
    validated = ARGS["search_books"].model_validate_json(text)
    print("\n=== Валідований об'єкт Pydantic ===")
    print(validated)
except Exception as e:
    print(f"\nМодель або сервер не підтримує json_schema response_format: {e}")
