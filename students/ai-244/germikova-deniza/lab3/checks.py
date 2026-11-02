
import csv

from tools import PRODUCTS_FILE


FORBIDDEN_ACTIONS = {"place_order"}


def check_meaning(name: str, arguments: dict) -> tuple[bool, str]:
    """Перевіряє зміст аргументів інструментів кулінарного агента."""

    if name in FORBIDDEN_ACTIONS:
        return False, "Дія заборонена."

    if name == "product_info":
        product = arguments.get("product", "").strip()

        if not product:
            return False, "Назву продукту не вказано."

        try:
            with open(PRODUCTS_FILE, "r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                products = {
                    row["product"].strip().casefold()
                    for row in reader
                    if row.get("product")
                }
        except (OSError, KeyError) as error:
            return False, f"Не вдалося перевірити каталог продуктів: {error}"

        if product.casefold() not in products:
            return False, f"Продукт '{product}' відсутній у каталозі."

    if name == "scale_amount":
        amount = arguments.get("amount")
        base_servings = arguments.get("base_servings")
        target_servings = arguments.get("target_servings")

        if amount is not None and amount <= 0:
            return False, "Кількість інгредієнта має бути більшою за нуль."

        if base_servings is not None and base_servings <= 0:
            return False, "Початкова кількість порцій має бути більшою за нуль."

        if target_servings is not None and target_servings <= 0:
            return False, "Цільова кількість порцій має бути більшою за нуль."

    return True, "Перевірка пройдена."

