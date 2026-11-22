import config
from openai import OpenAI
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_dose"].model_json_schema()

prompts = [
    "У мене горщик на 3 літри, а доза добрива 5 мл на літр. Сформуй аргументи для розрахунку.",
    "Порахуй дозу для величезного горщика на 500 літрів при нормі 5 мл на літр.",
]

for p in prompts:
    print(f"ЗАПИТ: {p}")
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": p}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "args", "schema": schema},
        },
    )
    text = response.choices[0].message.content
    print("JSON від моделі:", text)
    try:
        validated = ARGS["calc_dose"].model_validate_json(text)
        print("Pydantic OK:", validated, "\n")
    except Exception as e:
        print("Pydantic Error:", e, "\n")