"""Додаткове завдання: запобігання помилкам на сервері через structured output."""
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_dose"].model_json_schema()

prompts = [
    "Порахуй дозу добрива для горщика об'ємом 3.5 літри при нормі 6 мл на літр.",
    "Порахуй дозу добрива для горщика об'ємом мінус 5 літрів при нормі 6 мл на літр.",
]

for p in prompts:
    print(f"ЗАПИТ: {p}")
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": p}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "calc_dose_args", "schema": schema},
        },
        temperature=0.0,
    )
    text = response.choices[0].message.content
    print("JSON від моделі:", text)
    try:
        validated = ARGS["calc_dose"].model_validate_json(text)
        print("Pydantic OK:", validated)
    except Exception as e:
        print("Pydantic ERROR:", e)
    print("-" * 50)
