"""Формування довгого завдання для лабораторної роботи №4.

Варіант 9 — вибір ноутбука.
Для кожної з шести моделей:
(а) пошук інформації в корпусі;
(б) отримання ціни з довідника;
(в) розрахунок розстрочки.

Мінімальна кількість викликів інструментів: 6 * 3 = 18.
"""

import json
import re

from tools import search_laptops, laptop_info, calc_installment


MODELS = [
    "StudyNova 14",
    "CodeNova 15",
    "GameNova X16",
    "DesignNova 16",
    "OfficeNova 14",
    "StudyNova 15",
]

MONTHS = 12
OVERPAY_PERCENT = 10
MIN_CALLS = len(MODELS) * 3


def get_price(text):
    """Витягує ціну з текстової відповіді laptop_info."""
    match = re.search(
        r"Ціна:\s*(\d+(?:[.,]\d+)?)",
        str(text),
        flags=re.IGNORECASE,
    )

    if not match:
        raise ValueError(
            f"Не вдалося отримати ціну: {text}"
        )

    return float(match.group(1).replace(",", "."))


def get_payment(text):
    """Витягує щомісячний платіж із відповіді calc_installment."""
    match = re.search(
        r"(\d+(?:[.,]\d+)?)\s*грн\s+на\s+місяць",
        str(text),
        flags=re.IGNORECASE,
    )

    if not match:
        raise ValueError(
            f"Не вдалося отримати платіж: {text}"
        )

    return float(match.group(1).replace(",", "."))


def compute():
    """Обчислює еталонну відповідь прямими викликами інструментів."""
    details = []
    total_payment = 0.0

    for model in MODELS:
        # (а) Пошук у корпусі.
        search_result = str(search_laptops(model))

        if model.lower() not in search_result.lower():
            raise ValueError(
                f"Модель {model} не знайдена: {search_result}"
            )

        # (б) Отримання ціни з довідника.
        info_result = laptop_info(model)
        price = get_price(info_result)

        # (в) Розрахунок розстрочки.
        installment_result = calc_installment(
            price,
            MONTHS,
            OVERPAY_PERCENT,
        )
        payment = get_payment(installment_result)

        total_payment += payment

        details.append(
            {
                "model": model,
                "price": price,
                "monthly_payment": payment,
            }
        )

    return round(total_payment, 2), details


def make_question():
    """Формує питання за шаблоном таблиці 6 методички."""
    models_text = ", ".join(MODELS)

    return (
        f"Для кожної з шести моделей ноутбуків: {models_text}. "
        "Для кожної: "
        "(а) знайди в корпусі інформацію про модель "
        "за допомогою search_laptops і наведи одним реченням; "
        "(б) знайди в довіднику ціну моделі "
        "за допомогою laptop_info; "
        "(в) порахуй щомісячний платіж "
        "за допомогою calc_installment "
        f"при розстрочці на {MONTHS} місяців "
        f"із переплатою {OVERPAY_PERCENT}%. "
        "Для кожної моделі наведи назву, ціну "
        "та щомісячний платіж. "
        "У кінці назви суму щомісячних платежів "
        "за всі шість ноутбуків одним числом у гривнях. "
        "Не пропускай жодної моделі. "
        "Використовуй усі три інструменти для кожної моделі. "
        "Не обчислюй розстрочку самостійно."
    )


def main():
    total, details = compute()

    task = {
        "id": "L1",
        "variant": 9,
        "question": make_question(),
        "expected": f"{total:.2f}",
        "details": details,
        "min_calls": MIN_CALLS,
        "months": MONTHS,
        "overpay_percent": OVERPAY_PERCENT,
    }

    with open(
        "long_task.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            task,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("Створено long_task.json")
    print(f"Кількість моделей: {len(MODELS)}")
    print(f"Мінімальна кількість викликів: {MIN_CALLS}")
    print(f"Очікувана сума: {total:.2f} грн")
    print(f"Кількість записів details: {len(details)}")
    print()
    print("ПИТАННЯ:")
    print(task["question"])


if __name__ == "__main__":
    main()
