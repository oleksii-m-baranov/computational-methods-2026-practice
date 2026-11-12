import sys
sys.stdout.reconfigure(encoding='utf-8')
from providers import make_client

client, model = make_client("local")

CREATIVE = "Назва платформи взаємного навчання студентів"
FACTUAL = "Рік відкриття пеніциліну Флемінгом"

def run(prompt, n=5, **params):
    answers = []
    for _ in range(n):
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **params,
        )
        answers.append(r.choices[0].message.content.strip())
    return answers

# Крок 2. Творче завдання — вплив temperature
print("=" * 60)
print("ТВОРЧЕ ЗАВДАННЯ — temperature")
print("=" * 60)
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    print(f"\ntemperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print(f"  • {a}")

# Крок 3. Творче завдання — вплив top_p
print("\n" + "=" * 60)
print("ТВОРЧЕ ЗАВДАННЯ — top_p (при temperature=0.7)")
print("=" * 60)
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    print(f"\ntop_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print(f"  • {a}")

# Крок 4. Фактичне питання — вплив temperature
print("\n" + "=" * 60)
print("ФАКТИЧНЕ ПИТАННЯ — temperature")
print("=" * 60)
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    print(f"\ntemperature={t}:")
    for a in answers:
        print(f"  • {a}")

# Крок 5. Перевірка відтворюваності
print("\n" + "=" * 60)
print("ПЕРЕВІРКА ВІДТВОРЮВАНОСТІ (10 запусків, temperature=0.0)")
print("=" * 60)
answers = run(FACTUAL, n=10, temperature=0.0)
print(f"Унікальних відповідей: {len(set(answers))}")
print(f"Усі відповіді однакові: {len(set(answers)) == 1}")
print(f"Відповіді: {answers}")
