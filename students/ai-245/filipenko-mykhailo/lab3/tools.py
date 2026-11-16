import csv
import os
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CORPUS_DIR = BASE_DIR / "data" / "corpus"
LAPTOPS_FILE = BASE_DIR / "data" / "laptops.csv"


def search_laptops(query: str) -> str:
    words = re.findall(r"\w+", query.casefold())

    if not words:
        return "Пошуковий запит порожній."

    stop_words = {
        "ноутбук", "ноутбуки", "ноутбука",
        "потрібен", "порадь", "знайди",
        "на", "для", "і", "та", "з",
        "складі", "ціна", "ціну", "коштує"
    }

    keywords = [
        word for word in words
        if word not in stop_words
    ]

    if not keywords:
        return f"За запитом '{query}' нічого не знайдено."

    if not CORPUS_DIR.is_dir():
        raise FileNotFoundError(
            f"Каталог документів не знайдено: {CORPUS_DIR}"
        )

    matches = []

    for filepath in sorted(CORPUS_DIR.iterdir()):
        if not filepath.is_file():
            continue

        text = filepath.read_text(encoding="utf-8")
        content = text.casefold()

        score = sum(
            1 for word in set(keywords)
            if word in content
        )

        if score > 0:
            lines = text.splitlines()
            title = lines[0].strip() if lines else filepath.name

            matches.append((score, title))

    if not matches:
        return f"За запитом '{query}' нічого не знайдено."

    matches.sort(key=lambda item: (-item[0], item[1]))

    return " | ".join(
        title for _, title in matches
    )


def laptop_info(model: str) -> str:
    if not LAPTOPS_FILE.is_file():
        raise FileNotFoundError(
            f"Файл каталогу не знайдено: {LAPTOPS_FILE}"
        )

    requested_model = model.strip().casefold()

    with LAPTOPS_FILE.open(
        encoding="utf-8-sig",
        newline=""
    ) as file:
        for row in csv.DictReader(file):
            catalog_model = row["model"].strip()

            if catalog_model.casefold() == requested_model:
                return (
                    f"Модель: {catalog_model}, "
                    f"ціна: {row['price']} грн, "
                    f"на складі: {row['in_stock']} шт., "
                    f"гарантія: {row['warranty_months']} міс."
                )

    return f"Моделі '{model}' немає в довіднику."


def calc_installment(
    price: float,
    months: float,
    overpay_percent: float
) -> str:
    if months <= 0:
        return (
            "Помилка: кількість місяців "
            "має бути більшою за нуль."
        )

    if price < 0:
        return "Помилка: ціна не може бути від'ємною."

    if overpay_percent < 0:
        return (
            "Помилка: відсоток переплати "
            "не може бути від'ємним."
        )

    total = price * (1 + overpay_percent / 100)
    monthly = total / months

    return (
        f"{monthly:.2f} грн на місяць, "
        f"усього {total:.2f} грн"
    )


def place_order(model: str) -> str:
    return (
        f"Оформлення замовлення для '{model}' "
        "заборонено."
    )


TOOLS = {
    "search_laptops": search_laptops,
    "laptop_info": laptop_info,
    "calc_installment": calc_installment,
    "place_order": place_order
}
