import csv
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def search_rules(query: str) -> str:
    q = query.lower()
    found = []

    folder = DATA_DIR / "corpus"

    for filename in sorted(os.listdir(folder)):
        with open(folder / filename, encoding="utf-8") as f:
            text = f.read()

        if q in text.lower():
            found.append(text.split("\n")[0])

    if not found:
        return f"За запитом '{query}' нічого не знайдено."

    return " | ".join(found)


def tariff_info(city: str) -> str:
    with open(DATA_DIR / "tariffs.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["city"].lower() == city.lower():
                return (
                    f"Ціна: {row['price_per_kg']} грн/кг, "
                    f"термін: {row['days']} днів, "
                    f"мінімальна вартість: {row['min_price']} грн"
                )

    return f"Міста '{city}' немає в довіднику тарифів."


def calc_price(
    weight: float,
    price_per_kg: float,
    min_price: float
) -> str:
    total = weight * price_per_kg

    if total < min_price:
        return f"{min_price} грн (спрацювала мінімальна вартість)"

    return f"{round(total, 2)} грн"


TOOLS = {
    "search_rules": search_rules,
    "tariff_info": tariff_info,
    "calc_price": calc_price,
}
