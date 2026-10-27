from providers import make_client

client, model = make_client("local")

CREATIVE = "Запропонуй креативну назву для мобільного застосунку нагадувань про ліки. Напиши лише назву."
FACTUAL = "Який рік відкриття Київського метрополітену? Відповідай лише роком."

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

print("=== ЕКСПЕРИМЕНТ 1: Temperature (Творче) ===")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, n=5, temperature=t)
    print(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()

print("=== ЕКСПЕРИМЕНТ 2: Top_p (Творче) ===")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, n=5, temperature=0.7, top_p=p)
    print(f"top_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()

print("=== ЕКСПЕРИМЕНТ 3: Temperature (Фактичне) ===")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, n=5, temperature=t)
    correct_count = sum(1 for a in answers if "1960" in a)
    print(f"temperature={t}: правильних {correct_count} з 5")
    print("   Відповіді:", answers)
    print()

print("=== ЕКСПЕРИМЕНТ 4: Перевірка відтворюваності ===")
answers_rep = run(FACTUAL, n=10, temperature=0.0)
unique_count = len(set(answers_rep))
all_same = (unique_count == 1)
print(f"Кількість запусків: 10")
print(f"Унікальних відповідей: {unique_count}")
print(f"Усі відповіді однакові: {all_same}")