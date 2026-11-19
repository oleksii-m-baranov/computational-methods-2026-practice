"""Інструменти агента. Варіант 2 — Кулінарія."""

import csv
import config
import rag


def search_docs(query: str) -> str:
    """Return only passages whose cosine similarity reaches the selected threshold."""
    candidates = rag.get_index().search(query, k=config.TOP_K)
    results = [row for row in candidates if row["score"] >= config.MIN_SCORE]
    rag.TRACE.append({"query": query, "results": results,
                      "top_score": candidates[0]["score"] if candidates else None})
    if not results:
        return "У документах нічого релевантного не знайдено."
    return "\n\n".join(
        f"[{row['source']}:{row['chunk']}; score={row['score']:.3f}] {row['text']}"
        for row in results
    )


def product_info(product: str) -> str:
    """Повертає калорійність і ціну продукту."""

    with open("data/products.csv", encoding="utf-8") as f:

        for row in csv.DictReader(f):

            if row["product"].lower() == product.lower():

                return (
                    f"Калорійність: {row['kcal_per_100g']} ккал "
                    f"на 100 г, ціна: {row['price_per_kg']} грн/кг"
                )

    return f"Продукту '{product}' немає в довіднику."


def scale_amount(
    amount: float,
    base_servings: float,
    target_servings: float,
) -> str:
    """Перераховує інгредієнти на іншу кількість порцій."""

    if base_servings <= 0:
        return (
            "Помилка: кількість порцій "
            "має бути більшою за нуль."
        )

    return str(
        round(amount * target_servings / base_servings, 1)
    )


def place_order(products: str) -> str:
    """
    Заборонений інструмент.

    Тестова заглушка без реального замовлення.
    """

    return "Тестова заглушка: реальне замовлення не виконується."


TOOLS = {
    "search_docs": search_docs,
    "product_info": product_info,
    "scale_amount": scale_amount,
    "place_order": place_order,
}
