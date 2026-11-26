
import json
from providers import local, LOCAL_MODEL

CREATIVE = (
    "Запропонуй назву застосунку нагадувань "
    "про ліки. Відповідай тільки назвою."
)

FACTUAL = (
    "Рік відкриття Київського метрополітену. "
    "Відповідай лише роком."
)


def run(prompt, n=5, **params):
    answers = []

    for i in range(n):
        r = local.chat.completions.create(
            model=LOCAL_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            **params
        )

        answer = (
            r.choices[0].message.content or ""
        ).strip()

        answers.append(answer)
        print(f"{i + 1}/{n}: {answer}")

    return answers


results = {
    "temperature": {},
    "top_p": {},
    "factual": {},
    "reproducibility": {}
}


# 1. Вплив temperature
for t in [0.0, 0.7, 1.5]:
    print(f"\nTemperature = {t}")

    answers = run(CREATIVE, temperature=t)

    results["temperature"][str(t)] = {
        "answers": answers,
        "unique": len(set(answers))
    }


# 2. Вплив top_p
for p in [0.1, 0.5, 1.0]:
    print(f"\nTop_p = {p}")

    answers = run(
        CREATIVE,
        temperature=0.7,
        top_p=p
    )

    results["top_p"][str(p)] = {
        "answers": answers,
        "unique": len(set(answers))
    }


# 3. Фактичне питання
for t in [0.0, 1.5]:
    print(f"\nФактичне питання, temperature={t}")

    answers = run(FACTUAL, temperature=t)

    correct = sum(
        a.strip().rstrip(".") == "1960"
        for a in answers
    )

    results["factual"][str(t)] = {
        "answers": answers,
        "correct": correct
    }


# 4. Відтворюваність
print("\nПеревірка відтворюваності")

answers = run(
    FACTUAL,
    n=10,
    temperature=0.0
)

results["reproducibility"] = {
    "answers": answers,
    "unique": len(set(answers)),
    "all_identical": len(set(answers)) == 1
}


with open(
    "sampling_results.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        results, f,
        ensure_ascii=False,
        indent=2
    )

print("\nРезультати збережено.")
