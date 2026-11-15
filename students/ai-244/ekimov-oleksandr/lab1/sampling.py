from providers import make_client

client, model = make_client("local")

CREATIVE = "Назва застосунку обліку особистих витрат"
FACTUAL = "Рік першого кінопоказу братів Люм’єр"


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

answers = run(FACTUAL, n=10, temperature=0.0)
print("Усі відповіді однакові:", len(set(answers)) == 1)