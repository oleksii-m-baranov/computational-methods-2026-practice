
from dispatcher import call_tool


TESTS = [
    (
        "1. Некоректний JSON",
        "search_laptops",
        '{"query":',
        "syntax"
    ),
    (
        "2. Неправильний тип",
        "search_laptops",
        '{"query": 123}',
        "schema"
    ),
    (
        "3. Відсутнє поле",
        "search_laptops",
        '{}',
        "schema"
    ),
    (
        "4. Зайве поле",
        "search_laptops",
        '{"query": "навчання", "extra": 1}',
        "schema"
    ),
    (
        "5. Невідомий інструмент",
        "unknown_tool",
        '{}',
        "name"
    ),
    (
        "6. Заборонена дія",
        "place_order",
        '{"model": "StudyNova 14"}',
        "permission"
    ),
    (
        "7. Неіснуюча модель",
        "laptop_info",
        '{"model": "UnknownLaptop999"}',
        "meaning"
    ),
    (
        "8. Значення поза межами",
        "calc_installment",
        '{"price": 22000, "months": 100, "overpay_percent": 10}',
        "schema"
    )
]


def main():
    passed = 0

    for title, name, arguments, expected in TESTS:
        level, result = call_tool(name, arguments)
        success = level == expected

        print(f"{title}: {'PASS' if success else 'FAIL'}")
        print(f"Очікується: {expected}")
        print(f"Отримано: {level}")
        print(f"Результат: {result}")
        print("-" * 50)

        if success:
            passed += 1

    print(f"ПІДСУМОК: {passed}/{len(TESTS)}")

    if passed != len(TESTS):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
