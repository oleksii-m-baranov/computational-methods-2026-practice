import json
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)

schema = ARGS["laptop_info"].model_json_schema()

response = client.chat.completions.create(
    model=config.MODEL,
    messages=[{"role": "user",
            "content": (
                "Сформуй аргументи для laptop_info. "
                "Значення поля model обов'язково має бути порожнім рядком ''. "
                "Не підставляй назву ноутбука."
            ),
        }
    ],
    response_format={"type": "json_schema",
        "json_schema": {"name": "args", "schema": schema}},
)

text = response.choices[0].message.content

print(text)
print(ARGS["laptop_info"].model_validate_json(text))