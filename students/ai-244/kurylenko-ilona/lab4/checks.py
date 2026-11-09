"""Перевірки змісту аргументів інструментів."""

import csv

with open("data/vaccines.csv", encoding="utf-8") as f:
    ROWS = list(csv.DictReader(f))
    VACCINES = {
        row["vaccine"].strip().lower(): row
        for row in ROWS
    }
    MIN_VACCINE_AGE = min(int(row["first_age_months"]) for row in ROWS)


def check_meaning(name, args):
    if name == "vaccine_info":
        has_vaccine = args.vaccine is not None and bool(args.vaccine.strip())
        has_age = args.age_months is not None

        if not has_vaccine and not has_age:
            return (
                "Помилка: для виклику vaccine_info потрібно вказати "
                "або вік кота в місяцях (age_months), або назву щеплення (vaccine)."
            )

        if has_vaccine:
            vaccine = args.vaccine.strip().lower()

            if vaccine not in VACCINES:
                return (
                    f"Помилка: щеплення '{args.vaccine}' "
                    "немає в довіднику. "
                    f"Доступні назви: {', '.join(VACCINES)}. "
                    "Порівняй назви за змістом, а не лише посимвольно. "
                    "Якщо у списку є щеплення з тим самим значенням, "
                    "повтори виклик vaccine_info з його точною назвою. "
                    "Якщо потрібно підібрати щеплення за віком кота, "
                    "передай вік у параметрі age_months. "
                    "Не відповідай, що щеплення недоступне, якщо "
                    "у довіднику є відповідна за змістом назва. "
                    "Якщо відповідного щеплення справді немає, "
                    "повідом користувачу про відсутність даних."
                )

        if has_age and args.age_months < MIN_VACCINE_AGE:
            return (
                f"Помилка: для віку {args.age_months} міс. щеплень у довіднику немає. "
                f"Перші щеплення в довіднику проводяться з {MIN_VACCINE_AGE} міс."
            )

    return None
