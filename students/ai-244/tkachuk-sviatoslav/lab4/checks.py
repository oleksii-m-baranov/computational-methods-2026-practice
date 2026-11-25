"""Предметні перевірки до запуску функції; дані ті самі, що в ЛР №2."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
with (ROOT / "data" / "vaccines.csv").open(encoding="utf-8", newline="") as f:
    VACCINES = {row["vaccine"].strip().casefold(): row for row in csv.DictReader(f)}


def check_meaning(name, args):
    if name == "search_articles":

        if not args.query.strip():
            return ("Помилка: порожній пошуковий запит. "
                    "Передай один-два змістовних ключових слова або скажи, що теми не вказано.")
    if name == "vaccine_info":
        if args.vaccine != args.vaccine.strip():
            return ("Помилка: у назві щеплення є зайві пробіли. "
                    "Введи точну назву без пробілів на початку й наприкінці.")
        key = args.vaccine.casefold()
        if key not in VACCINES:
            return (f"Помилка: щеплення '{args.vaccine}' немає в довіднику. "
                    f"Доступні: {', '.join(row['vaccine'] for row in VACCINES.values())}. "
                    "Виправ назву згідно з довідником або повідом, що даних немає.")



        row = VACCINES[key]
        try:
            age = int(row["first_age_months"])
        except (ValueError, TypeError):
            return ("Помилка: у графіку щеплень немає коректного віку. "
                    "Повідом користувачу, що графік потребує уточнення у ветеринара.")
        if age <= 0:
            return ("Помилка: вік у графіку щеплень має бути додатним. "
                    "Повідом користувачу, що графік потребує уточнення.")
    return None
