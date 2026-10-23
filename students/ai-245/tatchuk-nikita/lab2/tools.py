import csv
import math
import os


def search_works(query: str) -> str:
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


def material_info(material: str) -> str:
    with open("data/materials.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["material"].lower() == material.lower():
                return (f"Одиниця: {row['unit']}, ціна: {row['price']} грн, "
                        f"покриття: {row['coverage_m2']} м² на одиницю")
    return f"Матеріалу '{material}' немає в довіднику."


def calc_materials(area: float, coverage_m2: float, price: float) -> str:
    if coverage_m2 <= 0:
        return "Помилка: покриття має бути більшим за нуль."
    units = math.ceil(area / coverage_m2)
    return f"Потрібно одиниць: {units}, вартість: {round(units * price, 2)} грн"


TOOLS = {
    "search_works": search_works,
    "material_info": material_info,
    "calc_materials": calc_materials,
}
