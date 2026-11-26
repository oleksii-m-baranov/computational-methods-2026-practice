"""Додаткове завдання: запобігання помилкам на сервері (Structured Output)."""
from typing import Literal
from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)


class StrictScheduleArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    activity: Literal[
        "йога", "кардіо", "кросфіт", "пілатес", "розтяжка",
        "силове", "табата", "функціональне", "фітнес",
    ] = Field(description="Назва заняття з розкладу")


def run_structured(label, schema_model, prompt):
    schema = schema_model.model_json_schema()
    response = client.chat.completions.create(
        model=config.MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {"name": "args", "schema": schema},
        },
        temperature=0,
    )
    text = response.choices[0].message.content
    print(f"=== {label} ===")
    print("Запит :", prompt)
    print("Відповідь моделі:", text)
    try:
        parsed = schema_model.model_validate_json(text)
        print("Pydantic перевірка: OK ->", parsed)
    except ValidationError as e:
        print("Pydantic перевірка: ПОМИЛКА ->", e.errors()[0]["msg"])
    print()


if __name__ == "__main__":
    prompts = [
        "Порахуй витрату калорій за 45 хвилин тренування для людини вагою 75 кг.",
        "Скільки ккал спалить спортсмен масою 82.5 кг за півтори години з коефіцієнтом навантаження 8?",
        "Я важу 60 кілограмів і бігав 30 хв, порахуй калорії.",
    ]
    for i, p in enumerate(prompts, 1):
        run_structured(f"Тест calc_calories #{i}", ARGS["calc_calories"], p)

    # 3. Запит із заняттям, якого немає в Literal ("бокс" / "плавання")
    run_structured(
        "Тест значення поза Literal ('бокс')",
        StrictScheduleArgs,
        "Коли в розкладі є тренування з боксу? Сформуй аргументи пошуку розкладу.",
    )