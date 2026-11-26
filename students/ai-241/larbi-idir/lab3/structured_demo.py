from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calc_calories"].model_json_schema()

prompts = [
    "Скільки калорій я спалю за 45 хвилин тренування при вазі 70 кг? Сформуй аргументи.",
    "Порахуй витрату калорій для бігу (MET = 8) тривалістю 30 хв для людини вагою 65 кг.",
    "Порахуй калорії для тренування тривалістю -20 хвилин при вазі 70 кг.",
]

for prompt in prompts:
    print(f"ЗАПИТ: {prompt}")
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "calc_calories_args", "schema": schema},
        },
        temperature=0,
    )
    text = response.choices[0].message.content
    print("Відповідь моделі:", text)
    try:
        validated = ARGS["calc_calories"].model_validate_json(text)
        print("Pydantic OK:", validated)
    except Exception as e:
        print("Pydantic ERROR:", e)
    print("-" * 50)