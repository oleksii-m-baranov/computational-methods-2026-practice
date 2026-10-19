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


def schedule_info(activity: str) -> str:
    with open("data/schedule.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["activity"].lower() == activity.lower():
                return (f"День: {row['weekday']}, час: {row['time']}, "
                        f"тренер: {row['trainer']}")
    return f"Заняття '{activity}' немає в розкладі."


def calc_calories(minutes: float, weight_kg: float, met: float) -> str:
    return f"{round(met * 3.5 * weight_kg / 200 * minutes)} ккал"


TOOLS = {
    "search_exercises": search_exercises,
    "schedule_info": schedule_info,
    "calc_calories": calc_calories,
}
