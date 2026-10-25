from providers import make_client

client, model = make_client("llama")

CREATIVE = "Назва застосунку пошуку партнерів для тренувань"
FACTUAL = "Рік уведення гривні"

def run(prompt, n=5, **params):
    answers = []

    for _ in range(n):
        r = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            **params
        )

        answers.append(
            r.choices[0].message.content.strip()
        )

    return answers


print("\n=== TEMPERATURE ===")

for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)

    print(f"\ntemperature={t}")
    print(f"Унікальних: {len(set(answers))} з 5")

    for a in answers:
        print("-", a)


print("\n=== TOP_P ===")

for p in [0.1, 0.5, 1.0]:
    answers = run(
        CREATIVE,
        temperature=0.7,
        top_p=p
    )

    print(f"\ntop_p={p}")
    print(f"Унікальних: {len(set(answers))} з 5")

    for a in answers:
        print("-", a)


print("\n=== FACTUAL ===")

for t in [0.0, 1.5]:
    answers = run(
        FACTUAL,
        temperature=t
    )

    print(f"\ntemperature={t}")
    print(answers)


print("\n=== REPRODUCIBILITY ===")

answers = run(
    FACTUAL,
    n=10,
    temperature=0.0
)

print("Унікальних відповідей:", len(set(answers)))
print("Усі однакові:", len(set(answers)) == 1)