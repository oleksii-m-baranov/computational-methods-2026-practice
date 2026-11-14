import csv
import config
from tools import TOOLS

with open("data/products.csv", encoding="utf-8") as f:
    PRODUCTS = [row["product"] for row in csv.DictReader(f)]

def check_meaning(name, args):
    """
    Перевіряє зміст аргументів, які неможливо перевірити лише через Pydantic-схему.
    Повертає текст помилки для моделі або None, якщо все гаразд.
    """
    if name not in config.ALLOWED:
        return (
            f"Помилка: інструмент '{name}' заборонений або не існує. "
            f"Доступні інструменти: {', '.join(config.ALLOWED)}. "
            f"Не намагайся викликати заборонені дії."
        )

    if name == "product_info":
        product_name = getattr(args, "product", "")
        if product_name not in PRODUCTS:
            return (
                f"Помилка: продукту '{product_name}' немає в довіднику. "
                f"Точні назви продуктів можна дізнатися з пошуку або довідника."
            )

    return None