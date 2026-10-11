from providers import make_client

client, model = make_client("local")

CREATIVE = "Запропонуй оригінальну назву для сервісу доставки домашньої їжі. Напиши лише назву."
FACTUAL  = "Рік перших сучасних Олімпійських ігор. Відповідай лише роком."

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

print("Крок 2: Вплив temperature на творче завдання")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    print(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()

print("Крок 3: Вплив top_p на творче завдання")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    print(f"top_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()

print("Крок 4: Фактичне питання (temperature=0.0 та 1.5)")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t, n=5)
    print(f"temperature={t}:", answers)
    print(f"Кількість правильних ('1896'): {answers.count('1896')} з 5\n")

print("Крок 5: Перевірка відтворюваності")
answers_rep = run(FACTUAL, n=10, temperature=0.0)
print("Усі відповіді однакові:", len(set(answers_rep)) == 1)
print("Отримані відповіді:", answers_rep)