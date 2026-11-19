"""Додаткове завдання: перевірка structured output (response_format) на сервері."""

from openai import OpenAI
import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_dose"].model_json_schema()

prompts = [
    "Порахуй дозу добрива для горщика об'ємом 3 літри, якщо норма становить 5 мл на літр.",
    "Скільки мілілітрів добрива потрібно на 2.5 л води при концентрації 4 мл/л?",
    "Порахуй дозу добрива для від'ємного горщика -5 літрів при нормі 10 мл на літр.",
]

for q in prompts:
    print(f"Питання: {q}")
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": q}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "args", "schema": schema},
        },
        temperature=config.TEMPERATURE,
    )
    text = response.choices[0].message.content
    print("Сирий JSON від моделі:", text)
    try:
        parsed = ARGS["calc_dose"].model_validate_json(text)
        print("Pydantic OK:", parsed, "\n")
    except Exception as e:
        print("Pydantic ERROR:", e, "\n")