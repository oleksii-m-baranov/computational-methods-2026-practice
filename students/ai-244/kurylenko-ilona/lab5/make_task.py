"""Створення довгої задачі для варіанта 10: догляд за котом."""

import json

from tools import search_articles, vaccine_info, calc_food


# Шість котів різного віку та ваги з природно сформульованими потребами.
ITEMS = [
    (2, 2.0, "дряпає меблі"),
    (3, 3.0, "дряпає диван"),
    (4, 4.0, "не їсть"),
    (5, 5.0, "сильно линяє"),
    (6, 6.0, "правильне годування кота"),
    (7, 7.0, "як годувати кота"),
]

DAYS = 30
GRAMS_PER_KG = 25
MIN_CALLS = 18


def check_items():
    """Перевіряємо, що для кожного кота є стаття в корпусі та щеплення за віком."""
    for age, weight, need in ITEMS:
        article = search_articles(need)
        if "нічого не знайдено" in article:
            raise ValueError(f"Статтю не знайдено для потреби: {need}")

        info = vaccine_info(age_months=age)
        if "немає" in info or "Помилка" in info:
            raise ValueError(f"Не знайдено щеплення для віку {age} міс.: {info}")


def compute():
    """Обчислюємо правильний результат через інструменти, без моделі."""
    total = 0

    for age, weight, need in ITEMS:
        result = calc_food(weight, GRAMS_PER_KG, DAYS)
        grams = int(result.removesuffix(" г"))
        total += grams

    return total


def make_question():
    """Формуємо довге питання з шістьма позиціями за шаблоном методички."""
    descriptions = [
        f"{index}) кіт віком {age} міс., вагою {weight:g} кг ({need})"
        for index, (age, weight, need) in enumerate(ITEMS, start=1)
    ]

    question = (
        "Є шість котів різного віку й ваги:\n"
        + ";\n".join(descriptions)
        + ".\n"
        "Для кожного з шести котів: "
        "(а) знайди пораду з догляду щодо описаної потреби і наведи її одним реченням; "
        "(б) знайди в довіднику інформацію про щеплення за віком кота "
        "(назву, вік першого щеплення та ціну); "
        "(в) порахуй місячну кількість корму на 30 днів за нормою 25 г на 1 кг ваги на день. "
        "У кінці назви загальну кількість корму за місяць для всіх шести котів у грамах одним числом."
    )

    return question


def main():
    check_items()
    total = compute()

    task = {
        "id": "L1",
        "question": make_question(),
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
