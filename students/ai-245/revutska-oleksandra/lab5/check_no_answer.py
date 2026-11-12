
"""Перевірка поведінки RAG-агента за відсутності відповіді."""

import json

import agent


def main():
    with open("rag_cases.json", "r", encoding="utf-8") as file:
        cases = json.load(file)

    no_answer_cases = [
        case for case in cases
        if case["type"] == "no_answer"
    ]

    for case in no_answer_cases:
        print("\n" + "=" * 60)
        print("ТЕСТ:", case["id"])
        print("ЗАПИТАННЯ:", case["question"])

        answer = agent.run_agent(case["question"])

        print("\nВІДПОВІДЬ АГЕНТА:")
        print(answer)

        print("\nСТАТИСТИКА:")
        print("Кроки:", agent.LAST_RUN["steps"])
        print(
            "Виклики search_docs:",
            agent.LAST_RUN["search_docs_calls"],
        )
        print(
            "Усього токенів:",
            agent.LAST_RUN["total_tokens"],
        )

        print("\nОЦІНКА: потребує ручної перевірки")


if __name__ == "__main__":
    main()
