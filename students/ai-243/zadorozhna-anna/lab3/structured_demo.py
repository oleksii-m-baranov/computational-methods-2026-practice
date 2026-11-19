"""Демонстрація structured output: модель генерує аргументи за схемою."""
import json
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)

# беремо схему з класу ScaleAmountArgs
schema = ARGS["scale_amount"].model_json_schema()

# питання, яке провокує модель сформувати аргументи
QUESTION = (
    "У мене рецепт на 0 порцій і мінус 5 грамів інгредієнта. "
    "Сформуй аргументи для scale_amount. Спробуй передати саме ці значення."
)

response = client.chat.completions.create(
    model=config.MODEL,
    messages=[{"role": "user", "content": QUESTION}],
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "args", "schema": schema},
    },
)

text = response.choices[0].message.content
print("=== Сира відповідь моделі ===")
print(text)
print()

print("=== Перевірка Pydantic ===")
try:
    validated = ARGS["scale_amount"].model_validate_json(text)
    print("OK:", validated)
except Exception as e:
    print("FAIL:", e)