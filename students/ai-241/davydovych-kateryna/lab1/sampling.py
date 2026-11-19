from providers import make_client

client, model = make_client("local")   # llama3.2:3b

# Варіант 9. «Відповідай лише ...» додано, щоб відповіді можна було порівнювати
# на однаковість: інакше кожна відповідь різнитиметься хоча б одним словом пояснення.
CREATIVE = "Придумай назву для рекомендаційного сервісу фільмів. Відповідай лише назвою."
FACTUAL = "У якому році випущено перший iPhone? Відповідай лише роком."
CORRECT_YEAR = "2007"


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


print(f"===== Модель: {model} =====\n")

print("=== Крок 2. Творче завдання, вплив temperature ===")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    print(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()

print("=== Крок 3. Творче завдання, вплив top_p (temperature=0.7) ===")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    print(f"top_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()

print("=== Крок 4. Фактичне питання ===")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    correct = sum(CORRECT_YEAR in a for a in answers)
    print(f"temperature={t}: правильних {correct} з 5 -> {answers}")
print()

print("=== Крок 5. Відтворюваність (10 запусків, temperature=0.0) ===")
answers = run(FACTUAL, n=10, temperature=0.0)
print("Відповіді:", answers)
print("Унікальних:", len(set(answers)))
print("Усі відповіді однакові:", len(set(answers)) == 1)
