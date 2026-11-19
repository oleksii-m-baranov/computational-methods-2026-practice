import json
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["scale_amount"].model_json_schema()

response = client.chat.completions.create(
    model=config.MODEL,
    messages=[{"role": "user",
               "content": (
                "Рецепт містить 300 г рису на 4 порції. Потрібно приготувати 0 порцій. Сформуй аргументи для перерахунку."
            )}],
    response_format={"type": "json_schema",
                     "json_schema": {"name": "args", "schema": schema}},
)
text = response.choices[0].message.content
print(text)
print(ARGS["scale_amount"].model_validate_json(text))