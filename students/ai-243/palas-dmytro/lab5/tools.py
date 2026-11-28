"""Інструменти агента для предметної області «Ремонт квартири»."""
import csv
import math
import os
import config
import rag


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


def search_works(query: str) -> str:
    q = query.lower()
    found = []
    folder = "data/corpus"
    for filename in sorted(os.listdir(folder)):
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            text = f.read()
        if q in text.lower():
            found.append(text.split("\n")[0])
    if not found:
        return f"За запитом '{query}' нічого не знайдено."
    return " | ".join(found)


def material_info(material: str) -> str:
    with open("data/materials.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["material"].lower() == material.lower():
                return (f"Одиниця: {row['unit']}, ціна: {row['price']} грн, "
                        f"покриття: {row['coverage_m2']} м² на одиницю")
    return f"Матеріалу '{material}' немає в довіднику."


def calc_materials(area: float, coverage_m2: float, price: float) -> str:
    if coverage_m2 <= 0:
        return "Помилка: покриття має бути більшим за нуль."
    units = math.ceil(area / coverage_m2)
    return f"Потрібно одиниць: {units}, вартість: {round(units * price, 2)} грн"


def place_order(material: str, quantity: int) -> str:
    return f"Замовлення на '{material}' ({quantity} од.) оформлено"  # заглушка: агентові ця дія заборонена


TOOLS = {
    "search_works": search_works,
    "material_info": material_info,
    "calc_materials": calc_materials,
    "place_order": place_order,
    "search_docs": search_docs,
}
