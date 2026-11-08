
"""Додаткове завдання: structured output."""

import json

from openai import OpenAI

import config
from arguments import ARGS
from checks import check_meaning


client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY,
)

schema = ARGS["vaccine_info"].model_json_schema()

questions = [
    "Яка ціна комплексного щеплення? "
    "Сформуй аргументи для vaccine_info.",

    "У якому віці роблять перше щеплення від сказу? "
    "Сформуй аргументи для vaccine_info.",

    "Скільки коштує щеплення від котячого грипу? "
    "Сформуй аргументи для vaccine_info.",
]

for number, question in enumerate(questions, start=1):
    print(f"\n=== ТЕСТ {number} ===")
    print("Питання:", question)

    try:
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "vaccine_args",
                    "schema": schema,
                },
            },
            temperature=config.TEMPERATURE,
        )

        text = response.choices[0].message.content

        print("Відповідь моделі:", text)

        args = ARGS["vaccine_info"].model_validate_json(text)

        print("Pydantic: OK")
        print("Аргументи:", args.model_dump())

        problem = check_meaning("vaccine_info", args)

        if problem is None:
            print("Перевірка змісту: OK")
        else:
            print("Перевірка змісту:", problem)

    except Exception as error:
        print("ПОМИЛКА:", type(error).__name__, str(error))

