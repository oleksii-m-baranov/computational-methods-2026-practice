from providers import make_client

client, model = make_client("qwen")

CREATIVE = "Придумай назву сервісу доставки домашньої їжі. Лише назва, 1-2 слова."
FACTUAL = "Рік перших сучасних Олімпійських ігор. Відповідай лише роком."

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

print("Крок 2.")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    print(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print("  ", a)
    print()

print("Крок 3.")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    print(f"top_p={p}: унікальних {len(set(answers))} з 5")
print()

print("Крок 4.")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    print(f"temperature={t}:", answers)
print()

print("Крок 5")
answers = run(FACTUAL, n=10, temperature=0.0)
print("Усі відповіді однакові:", len(set(answers)) == 1)