from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calculate"].model_json_schema()

prompts = [
    "Порахуй штраф за 5 днів прострочення по 10 грн за день. Сформуй аргументи для обчислення.",
    "Додай 15 до 25. Сформуй аргументи для інструмента.",
    "Поділи 100 на 5. Сформуй аргументи для операції ділення.",  # значення поза Literal
]

for prompt in prompts:
    print(f"ЗАПИТ: {prompt}")
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "args", "schema": schema},
        },
        temperature=config.TEMPERATURE,
    )
    text = response.choices[0].message.content
    print("Відповідь моделі:", text)
    try:
        validated = ARGS["calculate"].model_validate_json(text)
        print("Pydantic OK:", validated)
    except Exception as e:
        print("Pydantic ERROR:", e)
    print("-" * 50)