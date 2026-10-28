"""Створення довгої задачі для варіанта 10: догляд за котом."""

import csv
import json
from pathlib import Path

from tools import search_articles, vaccine_info, calc_food


# Шість котів різного віку та ваги.
# Назви щеплень відповідають довіднику vaccines.csv.
ITEMS = [
    (2, 2.0, "комплексне"),
    (3, 3.0, "від сказу"),
    (3, 4.0, "каліцивіроз"),
    (4, 5.0, "хламідіоз"),
    (5, 6.0, "дерматофітія"),
    (6, 7.0, "інфекційний перитоніт"),
]

DAYS = 30
GRAMS_PER_KG = 25
MIN_CALLS = 18


def get_articles():
    """Беремо шість реальних назв статей з наявного корпусу."""
    folder = Path("data/corpus")
    files = sorted(folder.glob("*.txt"))

    if len(files) < 6:
        raise ValueError("У корпусі повинно бути щонайменше 6 статей.")

    titles = []
    for path in files[:6]:
        lines = path.read_text(encoding="utf-8").splitlines()
        title = lines[0].strip()
        if not title:
            raise ValueError(f"Порожня назва статті: {path.name}")
        titles.append(title)

    return titles


def check_vaccines():
    """Перевіряємо назви та вік першого щеплення."""
    with open("data/vaccines.csv", encoding="utf-8") as f:
        vaccines = {
            row["vaccine"]: row
            for row in csv.DictReader(f)
        }

    for age, weight, vaccine in ITEMS:
        if vaccine not in vaccines:
            raise ValueError(f"Немає щеплення: {vaccine}")

        first_age = int(vaccines[vaccine]["first_age_months"])
        if age < first_age:
            raise ValueError(
                f"Щеплення {vaccine} не підходить для віку {age} міс."
            )


def compute():
    """Обчислюємо правильний результат через інструменти."""
    total = 0

    for age, weight, vaccine in ITEMS:
        info = vaccine_info(vaccine)
        if "немає в довіднику" in info:
            raise ValueError(info)

        result = calc_food(weight, GRAMS_PER_KG, DAYS)
        grams = int(result.removesuffix(" г"))
        total += grams

    return total


def make_question(titles):
    """Формуємо довге питання з шістьма позиціями."""
    descriptions = []

    for index, ((age, weight, vaccine), title) in enumerate(
        zip(ITEMS, titles), start=1
    ):
        descriptions.append(
            f"{index}) кіт віком {age} міс., вагою {weight} кг; "
            f"тема статті: «{title}»; щеплення: «{vaccine}»"
        )

    question = (
        "Для кожного із шести котів виконай три дії за допомогою "
        "окремих інструментів. Не пропускай жодного кота. "
        "Дані котів:\n"
        + "\n".join(descriptions)
        + "\nДля КОЖНОГО кота: "
        "(а) виклич search_articles за вказаною темою та назви "
        "знайдену статтю; "
        "(б) виклич vaccine_info для вказаного щеплення "
        "та повідом вік першого щеплення і ціну; "
        "(в) виклич calc_food для розрахунку корму на 30 днів "
        "за нормою 25 грамів на кілограм ваги на день. "
        "Після обробки всіх шести котів назви загальну "
        "кількість корму за місяць у грамах одним числом. "
        "Не вигадуй дані та не обчислюй корм самостійно."
    )

    return question


def main():
    titles = get_articles()
    check_vaccines()

    for title in titles:
        result = search_articles(title)
        if "нічого не знайдено" in result:
            raise ValueError(f"Статтю не знайдено: {title}")

    total = compute()

    task = {
        "id": "L1",
        "question": make_question(titles),
        "expected": str(total),
        "min_calls": MIN_CALLS,
    }

    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)

    print("Правильна відповідь:", task["expected"])
    print("Мінімальна кількість викликів:", task["min_calls"])
    print("Файл long_task.json записано")


if __name__ == "__main__":
    main()