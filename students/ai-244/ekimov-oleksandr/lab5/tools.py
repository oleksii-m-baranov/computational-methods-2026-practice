"""Інструменти агента."""
import csv
import os

import config
import rag


def search_routes(query: str) -> str:
    q = query.lower()
    found = []
    folder = "data/corpus"
    if not os.path.exists(folder):
        return "Каталог корпусу не знайдено."
    for filename in sorted(os.listdir(folder)):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder, filename)
            with open(filepath, encoding="utf-8") as f:
                text = f.read()
            if q in text.lower():
                found.append(text.split("\n")[0].strip())
    if not found:
        return f"За запитом '{query}' нічого не знайдено."
    return " | ".join(found)


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


def transport_info(route: str) -> str:
    csv_path = "data/transport.csv"
    if not os.path.exists(csv_path):
        return "Файл довідника транспорту не знайдено."
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["route"].strip().lower() == route.strip().lower():
                return (f"Вартість: {row['price']} грн, "
                        f"час у дорозі: {row['hours']} год, "
                        f"рейсів на день: {row['departures']}")
    return f"Маршруту '{route}' немає в довіднику."


def calc_budget(price_per_person: float, people: float, extra: float) -> str:
    try:
        # Розрахунок загального бюджету (ціна в один бік * 2 боки * кількість людей + додаткові витрати)
        total = (float(price_per_person) * 2 * float(people)) + float(extra)
        return str(total)
    except Exception as e:
        return f"Помилка обчислення: {str(e)}"


def buy_ticket(ticket_id: str) -> str:
    """Заглушка для забороненої дії."""
    return "Квиток куплено"


TOOLS = {
    "search_routes": search_routes,
    "search_docs": search_docs,
    "transport_info": transport_info,
    "calc_budget": calc_budget,
    "buy_ticket": buy_ticket,
}