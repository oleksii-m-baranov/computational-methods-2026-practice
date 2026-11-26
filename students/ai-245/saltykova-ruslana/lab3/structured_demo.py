import json
from openai import OpenAI
import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)

schema = ARGS["scale_amount"].model_json_schema()

response = client.chat.completions.create(
    model=config.MODEL,
    messages=[{
        "role": "user",
        "content": "Треба перерахувати інгредієнти: було 3 порції і 600 грамів м'яса, а стане 6 порцій."
    }],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "scale_args",
            "schema": schema
        }
    },
)

text = response.choices[0].message.content
print("=== Відповідь моделі (JSON) ===")
print(text)

print("\n=== Результат валідації Pydantic ===")
print(ARGS["scale_amount"].model_validate_json(text))