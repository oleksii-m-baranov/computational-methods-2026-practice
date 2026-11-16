"""Додаткове завдання: запобігання помилкам на сервері (structured output)."""
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_installment"].model_json_schema()

prompts = [
    "Ноутбук коштує 24000 грн, розстрочка на 6 місяців з переплатою 10%. Сформуй аргументи для розрахунку розстрочки.",
    "Ноутбук за двадцять сім тисяч гривень у розстрочку на пів року без переплати. Сформуй аргументи для розрахунку розстрочки.",
    "Ноутбук коштує 52000 грн, розстрочка на 10 років (120 місяців) з переплатою 15%. Сформуй аргументи для розрахунку розстрочки.",
]

for p in prompts:
    print(f"Питання: {p}")
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": p}],
        temperature=config.TEMPERATURE,
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "args", "schema": schema},
        },
    )
    text = response.choices[0].message.content
    print(f"Сирий JSON : {text}")
    validated = ARGS["calc_installment"].model_validate_json(text)
    print(f"Pydantic OK: {validated}\n")
