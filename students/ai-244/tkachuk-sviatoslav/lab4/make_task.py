"""Формування довгої задачі для варіанта №10."""
import json
from pathlib import Path
from tools import calc_food, search_articles, vaccine_info

ROOT = Path(__file__).resolve().parent
ITEMS = [
    ("Мурчик", 2, 2.1, "годування", "комплексне"),
    ("Луна", 3, 2.7, "сказу", "від сказу"),
    ("Рижик", 4, 3.4, "переноску", "бордетельоз"),
    ("Сніжок", 6, 4.2, "збалансоване", "додаткове комплексне"),
    ("Соня", 14, 4.8, "активність", "панлейкопенія"),
    ("Барсик", 15, 5.5, "вода", "хламідіоз"),
]
MIN_CALLS = 18


def build_question():
    entries = [
        f"{name} — {age} міс., {weight:g} кг, пошук '{query}', щеплення '{vaccine}'"
        for name, age, weight, query, vaccine in ITEMS
    ]
    return (
        "Для кожного із шести котів виконай рівно три типи перевірок, окремими інструментами: "
        + "; ".join(entries) + ". "
        "Для кожного: (а) виклич search_articles з наведеним словом і наведи назву статті; "
        "(б) виклич vaccine_info для вказаної назви щеплення, наведи перший вік, інтервал і ціну; "
        "(в) виклич calc_food з вагою кота, нормою 25 г/кг/добу та 30 днями, наведи кількість грамів. "
        "Не пропускай позицій. У кінці назви сумарну витрату корму за 30 днів для шести котів в грамах одним числом. "
        "Це навчальна норма, не практична схема вакцинації чи харчування."
    )


def compute():
    total = 0
    for _, _, weight, query, vaccine in ITEMS:
        if "не знайдено" in search_articles(query) or "немає" in vaccine_info(vaccine):
            raise ValueError("Відсутні вхідні дані для позиції")
        total += int(calc_food(weight, 25, 30).split()[0])
    return total


def main():
    task = {"id": "L1", "question": build_question(), "expected": str(compute()), "min_calls": MIN_CALLS}
    (ROOT / "long_task.json").write_text(json.dumps(task, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Очікувана кількість корму: {task['expected']} г; мінімум викликів: {MIN_CALLS}")


if __name__ == "__main__":
    main()
