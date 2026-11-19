"""Завдання 6. Керування випадковістю: temperature і top_p."""
from providers import make_client, get_logger, save_json

log = get_logger()

client, model = make_client("local")

CREATIVE = "Придумай назву сервісу доставки домашньої їжі. Відповідай лише назвою."
FACTUAL = "Рік перших сучасних Олімпійських ігор? Відповідай лише роком."
CORRECT = "1896"


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


out = {"model": model, "temperature": {}, "top_p": {}, "factual": {}}

# Крок 2. Творче завдання, вплив temperature
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    print(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()
    out["temperature"][str(t)] = {"answers": answers, "unique": len(set(answers))}

# Крок 3. Творче завдання, вплив top_p
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    print(f"top_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)
    print()
    out["top_p"][str(p)] = {"answers": answers, "unique": len(set(answers))}

# Крок 4. Фактичне питання
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    correct = sum(CORRECT in a for a in answers)
    print(f"temperature={t}:", answers, f"правильних {correct}/5")
    out["factual"][str(t)] = {"answers": answers, "correct": correct}

# Крок 5. Перевірка відтворюваності
answers = run(FACTUAL, n=10, temperature=0.0)
same = len(set(answers)) == 1
print("Усі відповіді однакові:", same)
out["reproducibility"] = {"answers": answers, "unique": len(set(answers)), "all_same": same}

log.info(f"[sampling] {out}")
print("Збережено:", save_json("task6_sampling.json", out))
