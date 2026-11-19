"""Інструменти агента. Варіант 9 — Вибір ноутбука."""
import csv
import os

import config
import rag


def search_laptops(query: str) -> str:
    """Шукає ноутбуки в корпусі за ключовим словом або назвою моделі (без скорочення тексту)."""
    q = query.lower()
    found = []
    folder = "data/corpus"
    for filename in sorted(os.listdir(folder)):
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            text = f.read().strip()
        if q in text.lower():
            found.append(text)
    if not found:
        return f"За запитом '{query}' нічого не знайдено."
    return "\n\n".join(found)


def laptop_info(model: str) -> str:
    """Шукає модель у довіднику та повертає ціну, наявність і гарантію."""
    with open("data/laptops.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["model"].lower() == model.lower():
                return (f"Ціна: {row['price']} грн, "
                        f"на складі: {row['in_stock']} шт., "
                        f"гарантія: {row['warranty_months']} міс.")
    return f"Моделі '{model}' немає в довіднику."


def calc_installment(price: float, months: float,
                     overpay_percent: float) -> str:
    """Обчислює щомісячний платіж при розстрочці."""
    if months <= 0:
        return "Помилка: кількість місяців має бути більшою за нуль."
    total = price * (1 + overpay_percent / 100)
    return (f"{round(total / months, 2)} грн на місяць, "
            f"усього {round(total, 2)} грн")


def place_order(model: str) -> str:
    """Заглушка: оформлення замовлення агентові заборонено (табл. 7)."""
    return f"Замовлення на '{model}' оформлено"


def search_docs(query: str) -> str:
    """Векторний пошук по документах: повертає фрагменти разом з назвами файлів."""
    candidates = rag.get_index().search(query, config.TOP_K)
    found = [r for r in candidates if r["score"] >= config.MIN_SCORE]
    rag.TRACE.append({"query": query,
                      "top_score": candidates[0]["score"] if candidates else None,
                      "results": found})
    if not found:
        return "У документах нічого схожого не знайдено."
    return "\n\n".join(f"[{n}] Джерело: {r['source']}\n{r['text']}" for n, r in enumerate(found, 1))


TOOLS = {
    "search_laptops": search_laptops,
    "laptop_info": laptop_info,
    "calc_installment": calc_installment,
    "place_order": place_order,
    "search_docs": search_docs,
}
