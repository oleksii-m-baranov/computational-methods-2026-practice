"""Перевірки змісту аргументів."""
import csv

with open("data/laptops.csv", encoding="utf-8") as f:
    ROWS = list(csv.DictReader(f))

# моделі порівнюємо без урахування регістру, як це робить сам laptop_info
MODELS = {row["model"].lower() for row in ROWS}
PRICES = {float(row["price"]) for row in ROWS}


def check_meaning(name, args):
    """Повертає текст помилки для моделі або None, якщо все гаразд."""
    if name == "laptop_info":
        # у довіднику 11 моделей (більше десяти), тому не перелічуємо їх, а підказуємо, де взяти назву
        if args.model.lower() not in MODELS:
            return (f"Помилка: моделі '{args.model}' немає в довіднику. "
                    "Допустимі лише точні назви моделей з довідника; "
                    "їх можна дізнатися інструментом search_laptops. "
                    "Виправ назву або повідом користувачу, що даних про цю модель немає.")

    if name == "calc_installment":
        # ціна має бути взята з довідника, а не вигадана
        if args.price not in PRICES:
            return (f"Помилка: ціни {args.price:g} грн немає в довіднику, схоже, її вигадано. "
                    "Допустимі лише ціни моделей з довідника; "
                    "ціну обраної моделі повертає інструмент laptop_info. "
                    "Спершу виклич laptop_info для обраної моделі, а потім передай її ціну в calc_installment.")
    return None
