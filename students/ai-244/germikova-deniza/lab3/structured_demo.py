
from openai import OpenAI
from pydantic import ValidationError

import config
from arguments import ARGS
from checks import check_meaning

client = OpenAI(
    base_url=config.BASE_URL,
    api_key=config.API_KEY
)

tool_name = "product_info"
schema = ARGS[tool_name].model_json_schema()

tests = [
    ("Тест 1", "Сформуй аргументи product_info для продукту рис."),
    ("Тест 2", "Дізнайся ціну рису. Поверни JSON для product_info."),
    ("Тест 3", "Сформуй аргументи product_info для рису і додай поле color."),
    ("Тест 4", "Сформуй аргументи product_info для продукту 'неіснуючий продукт'. Збережи цю назву.")
]

for title, question in tests:
    print("\n" + "=" * 50)
    print(title)
    print("Запит:", question)

    try:
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "Поверни тільки JSON-аргументи product_info за схемою. Не змінюй назву продукту."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "ProductInfoArgs",
                    "schema": schema
                }
            },
            temperature=0
        )

        output = response.choices[0].message.content or ""
        print("Відповідь моделі:", output)

        try:
            args = ARGS[tool_name].model_validate_json(output)
            print("Pydantic: OK")

            valid, message = check_meaning(
                tool_name, args.model_dump()
            )
            print("Перевірка змісту:", "OK" if valid else message)

        except ValidationError as error:
            print("Pydantic: ПОМИЛКА")
            print(error)

    except Exception as error:
        print("Помилка:", error)

print("\nТестування завершено.")
