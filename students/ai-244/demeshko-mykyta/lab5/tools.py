import csv
import os

import config
import rag


def search_plants(query: str) -> str:
    q = query.lower()
    found = []
    folder = "data/corpus"
    for filename in sorted(os.listdir(folder)):
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            text = f.read()
        if q in text.lower():
            found.append(text.strip())
    if not found:
        return f"За запитом '{query}' нічого не знайдено."
    return "\n---\n".join(found)


def fertilizer_info(plant: str) -> str:
    with open("data/fertilizer.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["plant"].lower() == plant.lower():
                return (f"Доза: {row['dose_ml_per_liter']} мл на літр, "
                        f"періодичність: раз на "
                        f"{row['frequency_days']} днів")
    return f"Рослини '{plant}' немає в довіднику."


def calc_dose(pot_liters: float, dose_ml_per_liter: float) -> str:
    return f"{round(pot_liters * dose_ml_per_liter, 1)} мл"


def order_fertilizer(plant: str, amount_ml: float) -> str:
    return "Замовлення на добриво оформлено"  # Заглушка: агентові ця дія заборонена


def search_docs(query: str) -> str:
    """Векторний пошук по документах: повертає фрагменти разом з назвами файлів."""
    candidates = rag.get_index().search(query, config.TOP_K)
    found = [r for r in candidates if r["score"] >= config.MIN_SCORE]
    rag.TRACE.append({
        "query": query,
        "top_score": candidates[0]["score"] if candidates else None,
        "results": found,
    })
    if not found:
        return "У документах нічого схожого не знайдено."
    return "\n\n".join(f"[{n}] Джерело: {r['source']}\n{r['text']}" for n, r in enumerate(found, 1))


TOOLS = {
    "search_plants": search_plants,
    "fertilizer_info": fertilizer_info,
    "calc_dose": calc_dose,
    "order_fertilizer": order_fertilizer,
    "search_docs": search_docs,
}