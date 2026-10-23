"""Завдання 6. Керування випадковістю: temperature і top_p (варіант 8)."""
import json

from providers import make_client

client, model = make_client("local")

CREATIVE = "Придумай назву сервісу обміну речами. Відповідай лише однією назвою."
FACTUAL = "Рік першого польоту людини в космос. Відповідай лише роком."
CORRECT_YEAR = "1961"   # Ю. Гагарін, «Восток-1», 12 квітня 1961 р.


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


log = {}

# Крок 2. Творче завдання, вплив temperature
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    log[f"creative_temperature_{t}"] = answers
    print(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()

# Крок 3. Творче завдання, вплив top_p (температура фіксована)
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    log[f"creative_top_p_{p}"] = answers
    print(f"top_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()

# Крок 4. Фактичне питання
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    log[f"factual_temperature_{t}"] = answers
    correct = sum(CORRECT_YEAR in a for a in answers)
    print(f"temperature={t}: правильних {correct} з 5:", answers)

# Крок 5. Перевірка відтворюваності
answers = run(FACTUAL, n=10, temperature=0.0)
log["reproducibility_temperature_0.0"] = answers
print("Унікальних відповідей:", len(set(answers)))
print("Усі відповіді однакові:", len(set(answers)) == 1)

with open("sampling_results.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
