from providers import make_client

# Ініціалізуємо локальну модель (як і в попередніх завданнях)
client, model = make_client("local")

# Для Варіанта 5:
CREATIVE = "Запропонуй коротку креативну назву для застосунку пошуку партнерів для тренувань. Напиши лише назву."
FACTUAL  = "У якому році була введена гривня як національна валюта України? Відповідай лише роком."

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

print("=== ДОСЛІДЖЕННЯ TEMPERATURE (Творче завдання) ===")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    print(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()

print("=== ДОСЛІДЖЕННЯ TOP_P (Творче завдання) ===")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    print(f"top_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()

print("=== ФАКТИЧНЕ ПИТАННЯ ПРИ рiзнiй TEMPERATURE ===")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    print(f"temperature={t}:", answers)

print("=== ПЕРЕВІРКА ВІДТВОРЮВАНОСТІ (10 запусків при t=0.0) ===")
rep_answers = run(FACTUAL, n=10, temperature=0.0)
print("Усі відповіді однакові:", len(set(rep_answers)) == 1)
print("Отримані відповіді:", rep_answers)