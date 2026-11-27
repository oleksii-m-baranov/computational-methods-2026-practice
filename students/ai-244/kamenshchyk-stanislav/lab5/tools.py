import csv
import os

import config
import rag


def search_service(query: str) -> str:
    q = query.lower()
    found = []
    folder = "data/corpus"
    for filename in sorted(os.listdir(folder)):
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            text = f.read()
        if q in text.lower():
            found.append(text.strip())     # повний опис роботи з корпусу, без скорочення
    if not found:
        return f"За запитом '{query}' нічого не знайдено."
    return " | ".join(found)


def price_info(service: str) -> str:
    with open("data/prices.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["service"].lower() == service.lower():
                return (f"Робота: {row['work_price']} грн, "
                        f"деталь: {row['part_price']} грн за шт., "
                        f"нормо-годин: {row['hours']}")
    return f"Роботи '{service}' немає в прайсі."


def calc_total(work_price: float, part_price: float,
               quantity: float) -> str:
    return f"{round(work_price + part_price * quantity, 2)} грн"


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


def book_service(service: str, date_time: str = "") -> str:
    return f"Запис на '{service}' оформлено"  # заглушка: агентові ця дія заборонена


TOOLS = {
    "search_service": search_service,
    "price_info": price_info,
    "calc_total": calc_total,
    "search_docs": search_docs,
    "book_service": book_service,      # заборонена дія: немає в config.ALLOWED
}

