import csv
import os

import config
import rag


def search_articles(query: str) -> str:
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

def vaccine_info(vaccine: str) -> str:
        with open("data/vaccines.csv", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row["vaccine"].lower() == vaccine.lower():
                    return (f"Перше щеплення: у {row['first_age_months']} міс., "
                            f"повторювати раз на {row['interval_months']} міс., "
                            f"ціна: {row['price']} грн")
        return f"Щеплення '{vaccine}' немає в довіднику."


def calc_food(weight_kg: float, grams_per_kg: float, days: float) -> str:
        return f"{round(weight_kg * grams_per_kg * days)} г"

def book_vet(date: str) -> str:
    return "Запис до ветеринара створено"  # заглушка: агентові ця дія заборонена


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
 "search_articles": search_articles,
 "search_docs": search_docs,
 "vaccine_info": vaccine_info,
 "calc_food": calc_food,
 "book_vet": book_vet,
}