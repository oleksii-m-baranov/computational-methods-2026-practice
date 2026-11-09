import csv
import os


def search_plants(query: str) -> str:
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


def fertilizer_info(plant: str) -> str:
    with open("data/fertilizer.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["plant"].lower() == plant.lower():
                return (f"Доза: {row['dose_ml_per_liter']} мл на літр, "
                        f"періодичність: раз на "
                        f"{row['frequency_days']} днів")
    return f"Рослини '{plant}' немає в довіднику."


def calc_dose(pot_liters: float, dose_ml_per_liter: float) -> str:
    return f"{round(pot_liters * dose_ml_per_liter, 1)} мл"


TOOLS = {
    "search_plants": search_plants,
    "fertilizer_info": fertilizer_info,
    "calc_dose": calc_dose,
}