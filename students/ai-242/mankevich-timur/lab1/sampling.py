from providers import make_client

client, model = make_client("local")

# Варіант 2
CREATIVE = "Придумай одну назву застосунку нагадувань про ліки. Відповідай лише назвою."
FACTUAL = "Рік відкриття Київського метрополітену. Відповідай лише роком."


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


# Крок 2. Творче завдання, вплив temperature
print("=== Творче: temperature ===")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    print(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("  ", a)
    print()

# Крок 3. Творче завдання, вплив top_p (температура фіксована)
print("=== Творче: top_p ===")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    print(f"top_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("  ", a)
    print()

# Крок 4. Фактичне питання
print("=== Фактичне: temperature ===")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    print(f"temperature={t}:", answers)
print()

# Крок 5. Перевірка відтворюваності
print("=== Відтворюваність (10 запусків, temperature=0.0) ===")
answers = run(FACTUAL, n=10, temperature=0.0)
print("Унікальних відповідей:", len(set(answers)))
print("Усі відповіді однакові:", len(set(answers)) == 1)
