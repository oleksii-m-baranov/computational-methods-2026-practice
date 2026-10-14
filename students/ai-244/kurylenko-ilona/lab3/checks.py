
"""Перевірки змісту аргументів."""

import csv


with open("data/vaccines.csv", encoding="utf-8") as f:
    VACCINES = {
        row["vaccine"]: row
        for row in csv.DictReader(f)
    }


def check_meaning(name, args):
    if name == "vaccine_info":
        vaccine = args.vaccine.lower()

        if vaccine not in VACCINES:
            return (
                f"Помилка: щеплення '{args.vaccine}' немає в довіднику. "
                f"Доступні назви: {', '.join(VACCINES.keys())}. "
                "Використай точну назву щеплення з довідника "
                "або повідом користувачу, що даних немає."
            )

        # Перевірка віку першого щеплення за графіком
        row = VACCINES[vaccine]

        try:
            age = int(row["first_age_months"])
        except ValueError:
            return (
                f"Помилка: для щеплення '{vaccine}' "
                "вік у довіднику записано неправильно. "
                "Повідом користувачу, що дані потрібно перевірити."
            )

        if not 2 <= age <= 6:
            return (
                f"Помилка: для щеплення '{vaccine}' "
                f"вказано вік {age} міс., що виходить за межі "
                "графіка від 2 до 6 місяців. "
                "Повідом користувачу, що дані потрібно перевірити."
            )

    return None

