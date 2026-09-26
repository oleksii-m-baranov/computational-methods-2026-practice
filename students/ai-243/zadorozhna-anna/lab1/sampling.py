from providers import make_client

client, model = make_client("local")

CREATIVE = "Придумай назву для застосунку нагадувань про ліки. Лише назву, без пояснень."
FACTUAL  = "Рік відкриття Київського метрополітену. Відповідай лише роком."

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

# --- Шаг: Творче — temperature ---
print("-" * 60)
print("Творче завдання, вплив temperature")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    print(f"\ntemperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print(f"    - {a}")

# --- Шаг: Творче — top_p ---
print("-" * 60)
print("Творче завдання, вплив top_p ")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    print(f"\ntop_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print(f"    - {a}")

# --- Шаг : Фактичне ---
print("-" * 60)
print(" Фактичне питання")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    print(f"\ntemperature={t}:")
    for a in answers:
        print(f"    - {a}")
    print(f"    Правильних: {sum(1 for a in answers if '1960' in a)} з 5")

# --- Шаг : Відтворюваність ---
print("-" * 60)
print("Перевірка відтворюваності")
answers = run(FACTUAL, n=10, temperature=0.0)
print(f"Унікальних відповідей: {len(set(answers))}")
print(f"Усі відповіді однакові: {len(set(answers)) == 1}")
for a in set(answers):
    print(f"    - {a}")
