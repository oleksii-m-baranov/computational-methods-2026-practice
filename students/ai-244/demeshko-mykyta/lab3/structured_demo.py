from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_dose"].model_json_schema()

prompts = [
    "Порахуй добриво для горщика на 3 літри, якщо доза становить 2.5 мл на літр.",
    "Скільки треба добрива на 5 л при нормі 1.5 мл/л?",
    "Порахуй дозу для горщика на 500 літрів при нормі 2 мл/л.",
]

for p in prompts:
    print(f"Питання: {p}")
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": p}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "args", "schema": schema},
        },
    )
    text = response.choices[0].message.content
    print("Сирий JSON:", text)
    try:
        parsed = ARGS["calc_dose"].model_validate_json(text)
        print("Pydantic OK:", parsed)
    except Exception as e:
        print("Pydantic FAIL:", e)
    print("-" * 40)