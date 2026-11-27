"""Пошук статей, довідник щеплень і розрахунок корму."""
import csv
from pathlib import Path
import config
import rag

ROOT = Path(__file__).resolve().parent


def search_articles(query: str) -> str:
    found = []
    for path in sorted((ROOT / "data" / "corpus").glob("*.txt")):
        content = path.read_text(encoding="utf-8")
        if query.casefold() in content.casefold():
            found.append(content.strip())
    return "\n\n".join(found) if found else f"За запитом '{query}' нічого не знайдено."


def vaccine_info(vaccine: str) -> str:
    with (ROOT / "data" / "vaccines.csv").open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row["vaccine"].casefold() == vaccine.casefold():
                return (f"Перше щеплення: у {row['first_age_months']} міс., "
                        f"повторювати раз на {row['interval_months']} міс., "
                        f"ціна: {row['price']} грн")
    return f"Щеплення '{vaccine}' немає в довіднику."


def calc_food(weight_kg: float, grams_per_kg: float, days: float) -> str:
    return f"{round(weight_kg * grams_per_kg * days)} г"


def book_vet(date: str) -> str:
    return f"Запис до ветеринара на {date} створено"


def search_docs(query: str) -> str:
    candidates = rag.get_index().search(query, config.TOP_K)
    found = [item for item in candidates if item["score"] >= config.MIN_SCORE]
    rag.TRACE.append({"query": query, "top_score": candidates[0]["score"] if candidates else None,
                      "results": found})
    if not found:
        return "У документах нічого схожого не знайдено."
    return "\n\n".join(f"[{n}] Джерело: {item['source']}\n{item['text']}"
                       for n, item in enumerate(found, 1))

TOOLS = {
    "search_docs": search_docs,
    "search_articles": search_articles,
    "vaccine_info": vaccine_info,
    "calc_food": calc_food,
    "book_vet": book_vet,
}
