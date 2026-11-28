"""Перевірки змісту аргументів для автосервісу."""
import csv

with open("data/prices.csv", encoding="utf-8") as f:
    ROWS = list(csv.DictReader(f))

SERVICES = {row["service"].lower() for row in ROWS}
WORK_PRICES = {float(row["work_price"]) for row in ROWS}
PART_PRICES = {float(row["part_price"]) for row in ROWS}


def check_meaning(name, args):
    """Повертає текст помилки для моделі або None, якщо все гаразд."""
    if name == "price_info":
        if args.service.lower() not in SERVICES:
            return (
                f"Помилка: роботи '{args.service}' немає в прайсі. "
                "Допустимі лише точні назви робіт із прайсу; "
                "знайти доступні роботи можна інструментом search_service. "
                "Виправ назву роботи або повідом користувачу, що такої послуги немає."
            )

    if name == "calc_total":
        if args.work_price not in WORK_PRICES:
            return (
                f"Помилка: вартості роботи {args.work_price:g} грн немає в прайсі, схоже, її вигадано. "
                "Допустимі лише розцінки з прайсу, які повертає інструмент price_info. "
                "Спершу виклич price_info для потрібної роботи, а потім передай отримані ціни в calc_total."
            )
        if args.part_price not in PART_PRICES:
            return (
                f"Помилка: вартості деталі {args.part_price:g} грн немає в прайсі, схоже, її вигадано. "
                "Допустимі лише ціни деталей із прайсу, які повертає інструмент price_info. "
                "Спершу виклич price_info для потрібної роботи, а потім передай отримані ціни в calc_total."
            )

    return None
    