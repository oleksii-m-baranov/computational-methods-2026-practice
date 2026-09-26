import requests

MODEL = "llama3.2:3b"

CREATIVE = "Запропонуй назву застосунку для пішохідних екскурсій."
FACTUAL = "Рік відкриття будівлі Одеського оперного театру. Відповідай лише роком."


def run(prompt, n=5, **params):
    answers = []

    for i in range(n):
        print(f"  запуск {i + 1}/{n}...")

        options = {
            "num_predict": 50
        }

        options.update(params)

        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "stream": False,
                "options": options
            },
            timeout=300
        )

        response.raise_for_status()
        answer = response.json()["message"]["content"].strip()
        answers.append(answer)

    return answers


def show_results(title, answers):
    print(f"\n{title}")
    for i, answer in enumerate(answers, start=1):
        print(f"{i}. {answer}")

    print("Кількість унікальних відповідей:", len(set(answers)))


print("\n=== ТВОРЧЕ ЗАВДАННЯ: TEMPERATURE ===")

for temperature in [0.0, 0.7, 1.5]:
    answers = run(
        CREATIVE,
        n=5,
        temperature=temperature
    )

    show_results(
        f"temperature = {temperature}",
        answers
    )


print("\n=== ТВОРЧЕ ЗАВДАННЯ: TOP_P ===")

for top_p in [0.1, 0.5, 1.0]:
    answers = run(
        CREATIVE,
        n=5,
        temperature=0.7,
        top_p=top_p
    )

    show_results(
        f"top_p = {top_p}",
        answers
    )


print("\n=== ФАКТИЧНЕ ЗАВДАННЯ: TEMPERATURE ===")

for temperature in [0.0, 1.5]:
    answers = run(
        FACTUAL,
        n=5,
        temperature=temperature
    )

    show_results(
        f"temperature = {temperature}",
        answers
    )

    correct = sum(
        1
        for answer in answers
        if "1887" in answer
    )

    print("Правильних відповідей із 5:", correct)


print("\n=== ПЕРЕВІРКА ВІДТВОРЮВАНОСТІ ===")

answers = run(
    FACTUAL,
    n=10,
    temperature=0.0
)

show_results(
    "10 запусків при temperature = 0.0",
    answers
)

print(
    "Усі відповіді однакові:",
    len(set(answers)) == 1
)