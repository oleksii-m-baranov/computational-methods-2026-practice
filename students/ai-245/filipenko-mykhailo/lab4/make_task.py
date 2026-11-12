import json
import re

from tools import search_laptops, laptop_info, calc_installment

MODELS = [
    "StudyNova 14",
    "CodeNova 15",
    "GameNova X16",
    "DesignNova 16",
    "OfficeNova 14",
    "StudyNova 15"
]

MONTHS = 12
OVERPAY_PERCENT = 10


def get_price(text):
    match = re.search(r"Ціна:\s*(\d+(?:\.\d+)?)", text)

    if not match:
        raise ValueError(f"Не вдалося отримати ціну: {text}")

    return float(match.group(1))


def get_payment(text):
    match = re.search(r"([\d.]+)\s*грн на місяць", text)

    if not match:
        raise ValueError(f"Не вдалося отримати платіж: {text}")

    return float(match.group(1))


def main():
    details = []
    total_payment = 0

    for model in MODELS:
        search_result = search_laptops(model)

        if model.lower() not in search_result.lower():
            raise ValueError(
                f"Модель {model} не знайдена: {search_result}"
            )

        info_result = laptop_info(model)
        price = get_price(info_result)

        installment_result = calc_installment(
            price,
            MONTHS,
            OVERPAY_PERCENT
        )

        payment = get_payment(installment_result)
        total_payment += payment

        details.append({
            "model": model,
            "price": price,
            "monthly_payment": payment
        })

    question = (
        "Потрібно порівняти шість ноутбуків: "
        + ", ".join(MODELS)
        + ". Для КОЖНОЇ моделі окремо виконай "
        "search_laptops із точною назвою моделі, "
        "потім laptop_info, а потім calc_installment. "
        f"Розрахуй розстрочку на {MONTHS} місяців "
        f"із переплатою {OVERPAY_PERCENT}%. "
        "Виведи для кожної моделі ціну та щомісячний платіж. "
        "Наприкінці обчисли суму шести щомісячних платежів, "
        "якщо купити всі шість ноутбуків одночасно. "
        "Не пропускай жодної моделі та не обчислюй "
        "розстрочку самостійно."
    )

    task = {
        "variant": 9,
        "question": question,
        "expected": {
            "total_monthly_payment": round(total_payment, 2),
            "details": details
        },
        "min_calls": 18,
        "months": MONTHS,
        "overpay_percent": OVERPAY_PERCENT
    }

    with open("long_task.json", "w", encoding="utf-8") as file:
        json.dump(task, file, ensure_ascii=False, indent=2)

    print("Створено long_task.json")
    print(f"Кількість моделей: {len(MODELS)}")
    print(f"Мінімальна кількість викликів: {task['min_calls']}")
    print(f"Очікувана сума платежів: {total_payment:.2f} грн")


if __name__ == "__main__":
    main()
