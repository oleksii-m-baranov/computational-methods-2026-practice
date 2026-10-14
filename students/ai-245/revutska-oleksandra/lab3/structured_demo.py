import json

from openai import OpenAI
from pydantic import ValidationError

import config
from arguments import ARGS


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
)

schema = ARGS["calculate"].model_json_schema()

response = client.chat.completions.create(
    model=config.MODEL,
    messages=[
        {
            "role": "user",
            "content": (
                "Обчисли штраф 15 грн за день "
                "протягом 5 днів. "
                "Сформуй аргументи для calculate."
            ),
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "calculate_args",
            "schema": schema,
        },
    },
)

text = response.choices[0].message.content

print("=== СТРУКТУРОВАНА ВІДПОВІДЬ МОДЕЛІ ===")
print(text)

print("\n=== ПЕРЕВІРКА PYDANTIC ===")

try:
    data = json.loads(text)
    validated = ARGS["calculate"].model_validate(data)

    print("Статус: OK")
    print("Аргументи:", validated.model_dump())

except (json.JSONDecodeError, ValidationError) as error:
    print("Статус: ERROR")
    print(error)