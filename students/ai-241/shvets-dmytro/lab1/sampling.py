from providers import make_client

client, model = make_client("local")

CREATIVE = "Запропонуй назву застосунку нагадувань про ліки. Відповідай тільки назвою."
FACTUAL = "Рік відкриття Київського метрополітену. Відповідай лише роком."

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

print("=== Temperature Tests ===")
for t in [0.0, 0.7, 1.5]:
    ans = run(CREATIVE, temperature=t)
    print(f"temp={t}: unique={len(set(ans))}/5 -> {ans}")

print("\n=== Top_P Tests ===")
for p in [0.1, 0.5, 1.0]:
    ans = run(CREATIVE, temperature=0.7, top_p=p)
    print(f"top_p={p}: unique={len(set(ans))}/5 -> {ans}")

print("\n=== Factual Tests ===")
for t in [0.0, 1.5]:
    ans = run(FACTUAL, temperature=t)
    print(f"temp={t}: {ans}")

print("\n=== Reproducibility Test ===")
ans_rep = run(FACTUAL, n=10, temperature=0.0)
print(f"All identical: {len(set(ans_rep)) == 1} ({set(ans_rep)})")