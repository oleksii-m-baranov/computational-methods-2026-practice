"""Функції інструментів та реєстр (Варіант 7 + RAG search_docs)."""
import csv
import os

import config
import rag


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
    return "\n\n".join(
        f"[{n}] Джерело: {r['source']}\n{r['text']}" for n, r in enumerate(found, 1)
    )


def search_routes(query: str) -> str:
    filepath = "data/transport.csv"
    if not os.path.exists(filepath):
        return f"Помилка: файл '{filepath}' не знайдено."

    q = query.lower()
    found = []

    with open(filepath, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            r_lower = row["route"].lower()
            desc_lower = row.get("description", "").lower()

            if q in r_lower or q in desc_lower:
                found.append(row["route"])

    if not found:
        return f"За запитом '{query}' нічого не знайдено."

    return " | ".join(found)


def route_info(route: str) -> str:
    filepath = "data/transport.csv"
    if not os.path.exists(filepath):
        return f"Помилка: файл '{filepath}' не знайдено."

    with open(filepath, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["route"].lower() == route.lower():
                return (
                    f"Маршрут: {row['route']}, "
                    f"вартість проїзду: {row['price']} грн, "
                    f"час у дорозі: {row['hours']} год, "
                    f"рейсів на день: {row['departures']}"
                )

    return f"Маршруту '{route}' немає в довіднику."


def calculate_trip(price_per_person: float, people: int, extra: float) -> str:
    try:
        total = round(float(price_per_person) * int(people) + float(extra), 2)
        return f"Загальний бюджет поїздки: {total} грн"
    except Exception as e:
        return f"Помилка обчислення: {e}"


def buy_tickets(route: str, people: int) -> str:
    return (
        "Вибачте, але купівля квитків через цей сервіс недоступна. "
        "Агент може лише підбирати маршрути та рахувати бюджет."
    )


TOOLS = {
    "search_routes": search_routes,
    "route_info": route_info,
    "calculate_trip": calculate_trip,
    "buy_tickets": buy_tickets,
    "search_docs": search_docs,
}