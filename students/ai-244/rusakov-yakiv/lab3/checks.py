"""Перевірки змісту аргументів."""
import csv

with open("data/prices.csv", encoding="utf-8") as f:
    PRICES = list(csv.DictReader(f))

SERVICES = [row["service"].lower() for row in PRICES]
# пари (вартість роботи, вартість деталі), які реально існують у прайсі
PRICE_PAIRS = {(float(row["work_price"]), float(row["part_price"])) for row in PRICES}


def check_meaning(name, args):
    # Ключ довідника. Робіт 11 (>10), тому всі не перелічуємо — вказуємо, як знайти правильну назву.
    if name == "price_info":
        if args.service.strip().lower() not in SERVICES:
            return (f"Помилка: роботи '{args.service}' немає в прайсі. "
                    "Назва має збігатися з прайсом дослівно; точну назву можна дізнатися "
                    "інструментом search_service. "
                    "Виправ назву або повідом користувачу, що даних про цю роботу немає.")

    # Правило з кількох аргументів: ціни мають бути взяті з прайсу, а не вигадані.
    if name == "calc_total":
        if (args.work_price, args.part_price) not in PRICE_PAIRS:
            return (f"Помилка: ціни роботи {args.work_price} грн і деталі {args.part_price} грн "
                    "не збігаються з жодним рядком прайсу. "
                    "Передавай лише ціни, які повернув інструмент price_info, без змін. "
                    "Спершу виклич price_info для потрібної роботи.")
    return None
