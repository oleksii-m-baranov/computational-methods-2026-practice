import csv
import os
import rag
import config

def search_exercises(query: str) -> str:
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
    return " | ".join(found)


def schedule_info(activity: str) -> str:
    act = activity.strip().lower()
    with open("data/schedule.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["activity"].strip().lower() == act:
                return (f"День: {row['weekday']}, час: {row['time']}, "
                        f"тренер: {row['trainer']}")
    return f"Заняття '{activity}' немає в розкладі."


def calc_calories(minutes: float, weight_kg: float, met: float) -> str:
    return f"{round(met * 3.5 * weight_kg / 200 * minutes)} ккал"


def book_session(booking_id: str) -> str:
    return "записати на заняття"      # заглушка: агентові ця дія заборонена

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
    "search_exercises": search_exercises,
    "schedule_info": schedule_info,
    "calc_calories": calc_calories,
    "book_session": book_session,
    "search_docs": search_docs
}
