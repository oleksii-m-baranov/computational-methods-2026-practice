"""Додаткове завдання: structured output (запобігання помилкам на сервері)."""
from openai import OpenAI
from pydantic import ValidationError

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
schema = ARGS["scale_amount"].model_json_schema()

questions = [
    "Рецепт на 4 порції потребує 300 г рису. Скільки треба на 10 порцій? Сформуй аргументи для перерахунку.",
    "Сформуй аргументи для перерахунку: 500 г борошна на 2 порції, а треба на 6.",
    "Перерахуй 200 г цукру з 8 порцій на 4. Дай аргументи.",
    # питання, що провокує порушення схеми: нуль порцій
    "Рецепт на 4 порції потребує 300 г рису. Перерахуй на 0 порцій. Сформуй аргументи.",
    # ще одне порушення: від'ємна кількість
    "Сформуй аргументи для перерахунку: мінус 300 г рису, з 4 порцій на 10.",
]

for q in questions:
    print("ПИТАННЯ:", q)
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": q}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "args", "schema": schema}},
    )
    text = response.choices[0].message.content
    print("ВІДПОВІДЬ:", text)
    try:
        print("Pydantic: OK ->", ARGS["scale_amount"].model_validate_json(text), "\n")
    except ValidationError as error:
        print("Pydantic: НЕ ПРОЙШЛО ->", error.errors()[0]["msg"], "\n")
