
"""Перевірка якості RAG-пошуку."""

from rag import search_docs


TESTS = [
    ("Скільки книжок можна взяти додому?", "d01"),
    ("Коли працює читальна зала в суботу?", "d02"),
    ("Скільки коштує міжбібліотечне замовлення?", "d03"),
    ("Який річний бюджет на придбання книжок?", "d04"),
    ("Коли збирається літературний клуб Сторінка?", "d05"),
]


def main():
    correct = 0

    for number, (question, expected) in enumerate(TESTS, start=1):
        results = search_docs(question)

        found = any(
            result["id"].startswith(expected)
            for result in results
        )

        if found:
            correct += 1

        print(f"\nТест {number}: {question}")
        print(f"Очікуваний документ: {expected}")
        print(f"Результат: {'OK' if found else 'FAIL'}")

        for result in results:
            print(
                f"  {result['id']} | "
                f"score={result['score']:.3f}"
            )

    print(f"\nУспішних тестів: {correct}/{len(TESTS)}")


if __name__ == "__main__":
    main()
