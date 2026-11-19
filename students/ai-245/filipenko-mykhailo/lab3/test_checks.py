
"""Тестування перевірок AI-агента. ЛР3, варіант 9."""

from dispatcher import call_tool


TESTS = [
    (
        "1. Некоректний JSON",
        "search_laptops",
        '{"query":',
        "syntax",
        None
    ),
    (
        "2. Неправильний тип",
        "search_laptops",
        '{"query": 123}',
        "schema",
        None
    ),
    (
        "3. Відсутнє поле",
        "search_laptops",
        '{}',
        "schema",
        None
    ),
    (
        "4. Зайве поле",
        "search_laptops",
        '{"query": "навчання", "extra": 1}',
        "schema",
        None
    ),
    (
        "5. Невідомий інструмент",
        "unknown_tool",
        '{}',
        "name",
        None
    ),
    (
        "6. Заборонена дія",
        "place_order",
        '{"model": "StudyNova 14"}',
        "permission",
        None
    ),
    (
        "7. Неіснуюча модель",
        "laptop_info",
        '{"model": "UnknownLaptop999"}',
        "meaning",
        None
    ),
    (
        "8. Некоректна кількість місяців",
        "calc_installment",
        '{"price": 22000, "months": 0, "overpay_percent": 10}',
        "schema",
        None
    ),
    (
        "9. Непідтверджена ціна",
        "calc_installment",
        '{"price": 22000, "months": 6, "overpay_percent": 10}',
        "meaning",
        {}
    ),
    (
        "10. Невідповідність підтвердженій ціні",
        "calc_installment",
        '{"price": 8000, "months": 6, "overpay_percent": 10}',
        "meaning",
        {"verified_price": 22000}
    ),
    (
        "11. Правильна підтверджена ціна",
        "calc_installment",
        '{"price": 22000, "months": 6, "overpay_percent": 10}',
        "ok",
        {"verified_price": 22000}
    )
]


def main():
    passed = 0

    print("=" * 60)
    print("ТЕСТУВАННЯ ПЕРЕВІРОК ЛР3")
    print("=" * 60)

    for title, name, arguments, expected, context in TESTS:

        level, result = call_tool(
            name,
            arguments,
            context=context
        )

        success = level == expected

        print(f"\n{title}: {'PASS' if success else 'FAIL'}")
        print(f"Очікується: {expected}")
        print(f"Отримано: {level}")
        print(f"Результат: {result}")
        print("-" * 50)

        if success:
            passed += 1

    print("\n" + "=" * 60)
    print(f"ПІДСУМОК: {passed}/{len(TESTS)}")
    print("=" * 60)

    if passed != len(TESTS):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
