"""Інструменти кухонного агента."""
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RECIPES_DIR = BASE_DIR / "data" / "recipes"
PRODUCTS_FILE = BASE_DIR / "data" / "products.csv"


def search_recipes(query: str) -> str:
    """Шукає рецепти за назвою, типом, інгредієнтами або способом приготування."""
    query = query.strip().lower()

    if not query:
        return "Порожній пошуковий запит."

    found = []

    for path in sorted(RECIPES_DIR.glob("*.txt")):
        content = path.read_text(encoding="utf-8")
        if query in content.lower():
            first_line = content.splitlines()[0].strip()
            found.append(first_line)

    if not found:
        return f"За запитом '{query}' нічого не знайдено."

    return " | ".join(found)


def product_info(product: str) -> str:
    """Повертає калорійність і ціну продукту з каталогу."""
    product = product.strip().lower()

    if not PRODUCTS_FILE.exists():
        return "Каталог продуктів не знайдено."

    with PRODUCTS_FILE.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["product"].strip().lower() == product:
                return (
                    f"{row['product']}: "
                    f"{row['kcal_per_100g']} ккал на 100 г, "
                    f"{row['price_per_kg']} грн за кг."
                )

    return f"Продукт '{product}' відсутній у каталозі."


def scale_amount(
    amount: float,
    base_servings: float,
    target_servings: float,
) -> str:
    """Перераховує кількість інгредієнта на іншу кількість порцій."""
    if base_servings <= 0:
        return "Помилка: початкова кількість порцій має бути більшою за нуль."

    if target_servings <= 0:
        return "Помилка: цільова кількість порцій має бути більшою за нуль."

    scaled = amount * target_servings / base_servings
    return f"{scaled:g} г"