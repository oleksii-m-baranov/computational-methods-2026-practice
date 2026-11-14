import csv
import os
import rag

_INDEX = None


def _get_index():
    global _INDEX
    if _INDEX is None:
        _INDEX = rag.build_index()
    return _INDEX


def search_docs(query: str) -> str:
    idx = _get_index()
    results = idx.search(query)
    if not results:
        return (f"За запитом '{query}' у документах нічого не знайдено. "
                "Повідом користувачу, що цієї інформації немає в базі знань.")
    parts = []
    for r in results:
        parts.append(f"[{r['source']}#{r['chunk']}] (score={r['score']})\n{r['text']}")
    return "\n---\n".join(parts)


def search_plants(query: str) -> str:
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
    return f"Замовлення на {amount_ml} мл добрива для '{plant}' оформлено"


TOOLS = {
    "search_docs": search_docs,
    "search_plants": search_plants,
    "fertilizer_info": fertilizer_info,
    "calc_dose": calc_dose,
    "order_fertilizer": order_fertilizer,
}