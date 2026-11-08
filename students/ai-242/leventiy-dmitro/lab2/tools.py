import csv
import os


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

TOOLS = {
 "search_articles": search_articles,
 "vaccine_info": vaccine_info,
 "calc_food": calc_food,
}