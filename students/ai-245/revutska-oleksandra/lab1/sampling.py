from providers import make_client

client, model = make_client("local")

CREATIVE = "Запропонуй одну назву стартапу в галузі логістики. Відповідай лише назвою."
FACTUAL = "У якому році засновано Національний університет «Одеська політехніка»? Відповідай лише роком."


def run(prompt, n=5, **params):
    """Запускає промпт n разів і повертає список відповідей."""
    answers = []

    for _ in range(n):
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **params,
        )
        answers.append(r.choices[0].message.content.strip())

    return answers


print("=== 1. ВПЛИВ TEMPERATURE НА ТВОРЧЕ ЗАВДАННЯ ===")

for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)

    print(f"\ntemperature={t}: унікальних {len(set(answers))} з 5")

    for a in answers:
        print("  ", repr(a))


print("\n=== 2. ВПЛИВ TOP_P НА ТВОРЧЕ ЗАВДАННЯ ===")

for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)

    print(f"\ntop_p={p}: унікальних {len(set(answers))} з 5")

    for a in answers:
        print("  ", repr(a))


print("\n=== 3. ФАКТИЧНЕ ПИТАННЯ ===")

for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)

    print(f"\ntemperature={t}:")
    for a in answers:
        print("  ", repr(a))


print("\n=== 4. ВІДТВОРЮВАНІСТЬ ===")

answers = run(FACTUAL, n=10, temperature=0.0)

print("Відповіді:")
for a in answers:
    print("  ", repr(a))

print("Унікальних відповідей:", len(set(answers)))
print("Усі відповіді однакові:", len(set(answers)) == 1)