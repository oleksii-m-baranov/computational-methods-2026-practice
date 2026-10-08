from providers import make_client

client, model = make_client("local")

CREATIVE = "Придумай одну креативну назву для застосунку обліку особистих витрат. Відповідай лише назвою."
FACTUAL  = "Рік першого кінопоказу братів Люм'єр. Відповідай лише числом (роком)."

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

with open("sampling_results.txt", "w", encoding="utf-8") as f:
    f.write("=== Крок 2. Творче завдання, вплив temperature ===\n")
    for t in [0.0, 0.7, 1.5]:
        answers = run(CREATIVE, temperature=t)
        f.write(f"temperature={t}: унікальних {len(set(answers))} з 5\n")
        for a in answers:
            f.write(f"    {a}\n")
        f.write("\n")

    f.write("=== Крок 3. Творче завдання, вплив top_p ===\n")
    for p in [0.1, 0.5, 1.0]:
        answers = run(CREATIVE, temperature=0.7, top_p=p)
        f.write(f"top_p={p}: унікальних {len(set(answers))} з 5\n")
        for a in answers:
            f.write(f"    {a}\n")
        f.write("\n")

    f.write("=== Крок 4. Фактичне питання ===\n")
    for t in [0.0, 1.5]:
        answers = run(FACTUAL, temperature=t)
        f.write(f"temperature={t}: {answers}\n")

    f.write("\n=== Крок 5. Перевірка відтворюваності ===\n")
    answers = run(FACTUAL, n=10, temperature=0.0)
    f.write(f"Усі відповіді однакові: {len(set(answers)) == 1}\n")
    f.write(f"Унікальних відповідей: {len(set(answers))}\n")
