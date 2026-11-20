import csv
import os


def search_exercises(query: str) -> str:
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


def find_session(activity: str):
    """Перший рядок розкладу для заняття або None (використовує і make_task.py)."""
    with open("data/schedule.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["activity"].lower() == activity.lower():
                return row
    return None


def schedule_info(activity: str) -> str:
    row = find_session(activity)
    if row is None:
        return f"Заняття '{activity}' немає в розкладі."
    return (f"День: {row['weekday']}, час: {row['time']}, "
            f"тривалість: {row['duration_min']} хв, тренер: {row['trainer']}")


def calc_calories(minutes: float, weight_kg: float, met: float) -> str:
    return f"{round(met * 3.5 * weight_kg / 200 * minutes)} ккал"


def book_session(activity: str, weekday: str) -> str:
    return "Вас записано на заняття"      # заглушка: агентові ця дія заборонена


TOOLS = {
    "search_exercises": search_exercises,
    "schedule_info": schedule_info,
    "calc_calories": calc_calories,
    "book_session": book_session,
}
