from providers import make_client

# Використовуємо локальну модель llama3.2:3b або qwen3:4b
client, model = make_client("local")

CREATIVE = "Запропонуй одну коротку та оригінальну назву для рекомендаційного сервісу фільмів. Тільки назва."
FACTUAL = "У якому році був випущений перший iPhone? Відповідай лише одним числом (роком)."

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

print("=== 1. Творче завдання: Temperature ===")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    print(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("  -", a)
    print()

print("=== 2. Творче завдання: Top_p (при temperature=0.7) ===")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    print(f"top_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("  -", a)
    print()

print("=== 3. Фактичне питання: Temperature ===")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    print(f"temperature={t}:", answers)
print()

print("=== 4. Перевірка відтворюваності (10 запусків при t=0.0) ===")
repro_answers = run(FACTUAL, n=10, temperature=0.0)
print("Відповіді:", repro_answers)
print("Усі відповіді однакові:", len(set(repro_answers)) == 1)