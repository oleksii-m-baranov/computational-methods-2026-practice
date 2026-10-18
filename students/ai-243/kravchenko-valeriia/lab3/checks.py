"""Перевірки змісту аргументів."""
import csv

# Завантажуємо довідник міст один раз при старті
with open("data/tariffs.csv", encoding="utf-8") as f:
    CITIES = {row["city"] for row in csv.DictReader(f)}


def check_meaning(name, args):
    """Перевіряє сенс аргументів для конкретного інструмента.
    Повертає текст помилки для моделі або None, якщо все гаразд."""
    
    if name == "tariff_info":
        if args.city not in CITIES:
            return (f"Помилка: міста '{args.city}' немає в довіднику. "
                    f"Доступні міста: {', '.join(sorted(CITIES))}. "
                    "Виправ назву міста або повідом користувачу, "
                    "що даних про це місто немає.")
    
    if name == "search_rules":
        # Pydantic уже перевірив min_length/max_length для query,
        # тут можна додати специфічні правила для нашої області.
        # Наприклад, заборона на пошук "усього питання" цілком.
        if len(args.query.split()) > 5:
            return (f"Помилка: запит '{args.query}' занадто довгий (більше 5 слів). "
                    "Використовуй 1–2 ключові слова для пошуку правил.")
    
    if name == "calc_price":
        if args.weight <= 0:
            return ("Помилка: вага посилки має бути більшою за 0. "
                    "Перевір вагу в питанні користувача.")
        if args.price_per_kg <= 0 or args.min_price < 0:
            return ("Помилка: ціна за кілограм і мінімальна вартість "
                    "мають бути додатними. Візьми їх з результату tariff_info.")
    
    return None
    