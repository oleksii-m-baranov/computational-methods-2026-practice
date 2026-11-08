import json
from providers import make_client


TASKS = {
    "task1": "У якому році відкрили Київський метрополітен?",
    "task2": (
        'Поверни ТІЛЬКИ валідний JSON без markdown та пояснень '
        'у форматі {"city": "...", "year": ..., "lines_count": ...} '
        'для Києва.'
    ),
    "task3": (
        "Стисни текст до двох речень, зберігши всі числові значення: "
        "У 2024 році компанія перевезла 12500 тонн вантажу, "
        "виконавши 840 рейсів із 37 міст."
    ),
    "task4": (
        "Напиши функцію total_weight(items), яка приймає список словників "
        "із ключем weight і повертає суму всіх ваг. "
        "Використай Python."
    ),
    "task5": (
        "Є 120 коробок. 45 коробок важать по 8 кг, решта — по 12 кг. "
        "Вантажівка може перевозити не більше 1200 кг. "
        "Скільки рейсів потрібно зробити?"
    ),
    "task6": (
        "Поясни двома абзацами різницю між контейнерними та навалочними "
        "перевезеннями. Відповідай українською."
    ),
}


def ask(provider, task):
    client, model = make_client(provider)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": TASKS[task]}
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content


def main():
    results = {}

    for provider in ["llama", "qwen"]:
        results[provider] = {}

        for task in TASKS:
            print(f"{provider}: {task}")

            try:
                answer = ask(provider, task)

                results[provider][task] = {
                    "status": "success",
                    "response": answer,
                }

                print(answer)
                print()

            except Exception as e:
                results[provider][task] = {
                    "status": "error",
                    "error": str(e),
                }

                print(f"Помилка: {e}")
                print()

    with open("quality.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("Результати збережено у quality.json")


if __name__ == "__main__":
    main()