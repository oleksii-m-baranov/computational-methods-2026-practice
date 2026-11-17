import json
from providers import make_client

client, model = make_client("local")

CREATIVE = "Назва застосунку обліку особистих витрат"
FACTUAL = "Рік першого кінопоказу братів Люм'єр"


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

print("--- temperature (творче) ---")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    log[f"creative_temp_{t}"] = answers
    print(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)

print("--- top_p (творче) ---")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    log[f"creative_top_p_{p}"] = answers
    print(f"top_p={p}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("   ", a)

print("--- temperature (фактичне) ---")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    log[f"factual_temp_{t}"] = answers
    print(f"temperature={t}:")
    for a in answers:
        print("   ", a)

print("--- відтворюваність (temperature=0.0, 10 запусків) ---")
answers = run(FACTUAL, n=10, temperature=0.0)
log["repro_temp_0.0"] = answers
print("Унікальних відповідей:", len(set(answers)))
print("Усі відповіді однакові:", len(set(answers)) == 1)

with open("sampling_results.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
