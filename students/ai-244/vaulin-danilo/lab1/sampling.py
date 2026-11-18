from providers import make_client

client, model = make_client("local")

CREATIVE = "Назва стартапу в галузі логістики"
FACTUAL = "Рік заснування Національного університету «Одеська Політехніка»"


def run(prompt, n=5, **params):
    """Запускає промпт n разів і повертає список відповідей."""
    answers = []
    for _ in range(n):
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **params,
        )
        ans = r.choices[0].message.content.strip()
        answers.append(ans)
        print(".", end="", flush=True)
    print()
    return answers


print(f"=== Модель: {model} ===")

print("\n--- 1. Дослідження temperature (CREATIVE) ---")
for t in [0.0, 0.7, 1.5]:
    print(f"Запуск temperature={t} (5 прогонів):", end=" ")
    answers = run(CREATIVE, temperature=t)
    uniq = len(set(answers))
    print(f"-> temperature={t}: унікальних {uniq} з 5")
    for a in answers:
        print(f"   * {a}")

print("\n--- 2. Дослідження top_p (CREATIVE, temp=0.7) ---")
for p in [0.1, 0.5, 1.0]:
    print(f"Запуск top_p={p} (5 прогонів):", end=" ")
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    uniq = len(set(answers))
    print(f"-> top_p={p}: унікальних {uniq} з 5")
    for a in answers:
        print(f"   * {a}")

print("\n--- 3. Фактичне питання при t=0.0 та t=1.5 ---")
for t in [0.0, 1.5]:
    print(f"Запуск FACTUAL temperature={t} (5 прогонів):", end=" ")
    answers = run(FACTUAL, temperature=t)
    correct = sum(1 for a in answers if "1996" in a)
    print(f"-> FACTUAL temp={t}: правильних {correct} з 5 (унікальних {len(set(answers))})")
    for a in answers:
        print(f"   * {a}")

print("\n--- 4. Перевірка відтворюваності: FACTUAL, n=10, temperature=0.0 ---")
print("Запуск 10 прогонів:", end=" ")
rep_answers = run(FACTUAL, n=10, temperature=0.0)
all_same = len(set(rep_answers)) == 1
print(f"Усі 10 відповідей однакові: {all_same} (унікальних: {len(set(rep_answers))})")
for a in rep_answers:
    print(f"   * {a}")