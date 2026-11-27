import config
import rag
import csv
import os


def search_rules(query: str) -> str:
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
    return "\n\n".join(found)


def tariff_info(city: str) -> str:
    with open("data/tariffs.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["city"].lower() == city.lower():
                return (f"Ціна: {row['price_per_kg']} грн/кг, "
                        f"термін: {row['days']} днів, "
                        f"мінімальна вартість: {row['min_price']} грн")
    return f"Міста '{city}' немає в довіднику тарифів."


def calc_price(weight: float, price_per_kg: float,
               min_price: float) -> str:
    total = weight * price_per_kg
    if total < min_price:
        return f"{min_price} грн (спрацювала мінімальна вартість)"
    return f"{round(total, 2)} грн"


def cancel_parcel(parcel_id: str) -> str:
    return "Посилку скасовано"      # заглушка: агентові ця дія заборонена


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
    "search_docs": search_docs,
    "search_rules": search_rules,
    "tariff_info": tariff_info,
    "calc_price": calc_price,
    "cancel_parcel": cancel_parcel,
}
