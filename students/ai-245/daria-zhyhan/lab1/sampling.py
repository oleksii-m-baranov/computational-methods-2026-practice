
from providers import make_client

client, model = make_client("local")

CREATIVE = (
    "Придумай назву застосунку для пошуку "
    "партнерів для тренувань. Відповідай лише назвою."
)

FACTUAL = (
    "У якому році гривню ввели як національну "
    "валюту України? Відповідай лише роком."
)


def run(prompt, n=5, **params):
    answers = []

    for i in range(n):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            **params
        )

        answer = response.choices[0].message.content.strip()
        answers.append(answer)

    return answers



print("\n=== ТВОРЧЕ ЗАВДАННЯ: TEMPERATURE ===", flush=True)

creative_results = {}

for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    creative_results[t] = answers

    print(
        f"\ntemperature={t}: "
        f"унікальних {len(set(answers))} з 5",
        flush=True
    )

    for answer in answers:
        print("  ", answer, flush=True)



print("\n=== ТВОРЧЕ ЗАВДАННЯ: TOP_P ===", flush=True)

for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)

    print(
        f"\ntop_p={p}: "
        f"унікальних {len(set(answers))} з 5",
        flush=True
    )

    for answer in answers:
        print("  ", answer, flush=True)


print("\n=== ФАКТИЧНЕ ЗАПИТАННЯ ===", flush=True)

for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)

    correct = sum(
        answer.strip().rstrip(".") == "1996"
        for answer in answers
    )

    print(f"\ntemperature={t}", flush=True)
    print("Відповіді:", answers, flush=True)
    print(f"Правильних: {correct} з 5", flush=True)


print("\n=== ПЕРЕВІРКА ВІДТВОРЮВАНОСТІ ===", flush=True)

answers = run(FACTUAL, n=10, temperature=0.0)

print("Відповіді:", answers, flush=True)
print("Кількість запусків: 10", flush=True)
print("temperature: 0.0", flush=True)
print("Унікальних відповідей:", len(set(answers)), flush=True)
print(
    "Усі відповіді однакові:",
    "так" if len(set(answers)) == 1 else "ні",
    flush=True
)
