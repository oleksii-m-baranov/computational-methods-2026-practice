"""Додаткове завдання: запобігання помилкам на сервері (structured output)."""
from openai import OpenAI

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["calculate"].model_json_schema()

questions = [
    "Я затримав книжку на 5 днів, штраф 10 грн за день. Сформуй аргументи для обчислення штрафу.",
    "Додай два штрафи: 35 гривень та 15 гривень. Сформуй аргументи для обчислення.",
    "Книжку тримали 12 днів при дозволеному терміні 7 днів. Сформуй аргументи для підрахунку днів прострочення.",
    "Штраф 100 гривень треба поділити на 4 рівні частини. Сформуй аргументи для обчислення.",
]

for question in questions:
    print(f"Питання: {question}")
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": question}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "args", "schema": schema},
        },
    )
    text = response.choices[0].message.content
    print(text)
    print(ARGS["calculate"].model_validate_json(text))
    print("-" * 60)

