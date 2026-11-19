from providers import make_client

client, model = make_client("local")

CREATIVE = "Назва застосунку пішохідних екскурсій"
FACTUAL = "У якому році відкрили нинішню будівлю Одеського оперного театру?"

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

print("--- temperature (творче) ---")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    print(f"temperature={t}: унікальних {len(set(answers))} з 5")
    for a in answers:
        print(" ", a)

print("--- top_p (творче) ---")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    print(f"top_p={p}: унікальних {len(set(answers))} з 5")

print("--- temperature (фактичне) ---")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    print(f"temperature={t}:", answers)

print("--- відтворюваність ---")
answers = run(FACTUAL, n=10, temperature=0.0)
print("Усі відповіді однакові:", len(set(answers)) == 1)