import csv
import os
import config
import rag


def search_articles(query: str) -> str:
    q = query.strip().lower()
    found = []
    folder = "data/corpus"

    for filename in sorted(os.listdir(folder)):
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            text = f.read().strip()

        if q in text.lower():
            found.append(text)

    if not found:
        return f"За запитом '{query}' нічого не знайдено."

    return "\n\n".join(found)


def _format_vaccine(row: dict) -> str:
    return (
        f"{row['vaccine']} (перше щеплення з {row['first_age_months']} міс., "
        f"повторювати раз на {row['interval_months']} міс., "
        f"ціна: {row['price']} грн)"
    )


def vaccine_info(
    vaccine: str | None = None,
    age_months: int | None = None,
) -> str:
    """Довідка з навчального файла vaccines.csv.

    Правило пошуку за віком: показуємо щеплення, для яких вік кота
    не менший за first_age_months. Це довідка з навчальних даних,
    а не індивідуальне призначення.
    Якщо задано і назву, і вік: шукаємо за назвою та додаємо примітку,
    чи досяг кіт віку першого щеплення.
    """
    with open("data/vaccines.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if vaccine is not None and vaccine.strip():
        q = vaccine.strip().lower()
        for row in rows:
            if row["vaccine"].strip().lower() == q:
                text = "Щеплення " + _format_vaccine(row)
                if age_months is not None:
                    first = int(row["first_age_months"])
                    if age_months >= first:
                        text += f". Вік {age_months} міс. не менший за вік першого щеплення."
                    else:
                        text += f". Вік {age_months} міс. менший за вік першого щеплення."
                return text
        return f"Щеплення '{vaccine}' немає в довіднику."

    if age_months is not None:
        matched = sorted(
            (r for r in rows if int(r["first_age_months"]) <= age_months),
            key=lambda r: int(r["first_age_months"]),
        )
        if not matched:
            return f"У довіднику немає щеплень для віку {age_months} міс."
        return (
            f"За довідником (навчальні дані) для віку {age_months} міс. "
            "доступні щеплення, вік першого щеплення яких не більший за цей вік: "
            + "; ".join(_format_vaccine(r) for r in matched)
        )

    return "Помилка: вкажіть назву щеплення або вік кота в місяцях."

def calc_food(weight_kg: float, grams_per_kg: float, days: float) -> str:
    return f"{round(weight_kg * grams_per_kg * days)} г"


def book_vet(date: str) -> str:
    """Заборонена дія – заглушка для запису до ветеринара."""
    return f"Запис до ветеринара на {date} створено."


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
