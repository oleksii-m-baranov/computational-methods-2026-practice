"""Перевірки змісту аргументів інструментів."""

import csv

with open("data/vaccines.csv", encoding="utf-8") as f:
    VACCINES = {
        row["vaccine"].strip().lower(): row
        for row in csv.DictReader(f)
    }


def check_meaning(name, args):
    if name == "vaccine_info":
        vaccine = args.vaccine.strip().lower()

        if vaccine not in VACCINES:
            return (
                f"Помилка: щеплення '{args.vaccine}' "
                "немає в довіднику. "
                f"Доступні назви: {', '.join(VACCINES)}. "
                "Порівняй назви за змістом, а не лише посимвольно. "
                "Якщо у списку є щеплення з тим самим значенням, "
                "повтори виклик vaccine_info з його точною назвою. "
                "Не відповідай, що щеплення недоступне, якщо "
                "у довіднику є відповідна за змістом назва. "
                "Якщо відповідного щеплення справді немає, "
                "повідом користувачу про відсутність даних."
            )

    return None
