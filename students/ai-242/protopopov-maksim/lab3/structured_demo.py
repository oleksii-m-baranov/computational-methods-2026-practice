"""Додаткове завдання: structured output для інструментів варіанта 5 (догляд за рослинами).

Дві групи експериментів:
  A) calc_dose: числові межі з класу CalcDoseArgs (gt=0, le=100 / ge=0, le=50);
     питання поза межами показують, чи тримає сервер числові обмеження схеми.
  B) fertilizer_info з Literal: допустимі назви рослин беруться з data/fertilizer.csv;
     питання про рослину поза переліком показують, що робить модель, коли
     правильного значення в схемі немає.
"""
import csv
from typing import Literal

from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

import config
from arguments import ARGS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)

with open("data/fertilizer.csv", encoding="utf-8") as f:
    PLANTS = [row["plant"] for row in csv.DictReader(f)]


class FertilizerLiteralArgs(BaseModel):
    """Те саме, що FertilizerInfoArgs, але назва рослини обмежена переліком (Literal)."""
    model_config = ConfigDict(extra="forbid")
    plant: Literal[tuple(PLANTS)] = Field(
        description="Точна назва рослини з довідника підживлення"
    )


EXPERIMENTS = [
    # (назва групи, клас аргументів, список питань)
    (
        "A. calc_dose (числові межі)",
        ARGS["calc_dose"],
        [
            # коректні
            "Горщик на 3 літри, доза добрива 5 мл на літр.",
            "Рослина стоїть у горщику об'ємом 2.5 літра, добриво дозується по 4 мл на літр.",
            "Великий горщик на 10 літрів, доза 7 мл на літр.",
            # поза межами схеми
            "Горщик об'ємом 500 літрів, доза 5 мл на літр.",       # pot_liters > 100
            "Горщик на мінус 3 літри, доза 5 мл на літр.",         # pot_liters <= 0
            "Горщик на 2 літри, доза добрива 80 мл на літр.",      # dose > 50
        ],
    ),
    (
        "B. fertilizer_info з Literal (назви з довідника)",
        FertilizerLiteralArgs,
        [
            # коректні
            "Як часто підживлювати Фікус Бенджаміна?",
            "Яка доза добрива потрібна для Монстери Адансона?",
            # рослини, яких немає в довіднику (поза Literal)
            "Яка доза добрива потрібна для кактуса сагуаро?",
            "Як підживлювати орхідею фаленопсис?",
        ],
    ),
]

for group_name, args_class, queries in EXPERIMENTS:
    schema = args_class.model_json_schema()
    print("=" * 70)
    print(group_name)
    print("=" * 70)

    for query in queries:
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=[
                {
                    "role": "user",
                    "content": f"{query} Сформуй аргументи для інструмента.",
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "tool_args",
                    "strict": True,
                    "schema": schema,
                },
            },
        )

        text = response.choices[0].message.content
        print("---------------------------------------")
        print(f"Питання: {query}")
        print("Згенерований JSON моделі:")
        print(text)

        try:
            validated = args_class.model_validate_json(text)
            print("Pydantic: ПРОЙШОВ ->", validated)
        except ValidationError as error:
            print("Pydantic: НЕ ПРОЙШОВ ->")
            print(error)
        print()
