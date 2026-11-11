from providers import make_client

client, model = make_client("local")

# Варіант 1
CREATIVE = "Назва стартапу в галузі логістики"
FACTUAL = 'Рік заснування Національного університету "Одеська Політехніка"'
CORRECT_YEAR = "1918"   # перевірте в авторитетному джерелі і вкажіть посилання у звіті


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


def count_correct(answers):
    """Скільки відповідей містять правильний рік."""
    return sum(1 for a in answers if CORRECT_YEAR in a)


print(f"Модель: {model}")

print("\n===== Крок 2. Творче завдання: вплив temperature =====")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    print(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()

print("\n===== Крок 3. Творче завдання: вплив top_p (temperature=0.7) =====")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    print(f"top_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()

print("\n===== Крок 4. Фактичне питання =====")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    print(f"temperature={t}: правильних ({CORRECT_YEAR}) {count_correct(answers)} з 5")
    for a in answers:
        print("   ", a)
    print()

print("\n===== Крок 5. Відтворюваність (10 запусків, temperature=0) =====")
answers = run(FACTUAL, n=10, temperature=0.0)
print("Унікальних відповідей:", len(set(answers)))
print("Усі відповіді однакові:", len(set(answers)) == 1)
for a in answers:
    print("   ", a)
