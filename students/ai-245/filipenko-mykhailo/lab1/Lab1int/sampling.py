import json
from pathlib import Path
from providers import make_client

client, model = make_client("llama")

CREATIVE = (
    "Придумай коротку оригінальну назву "
    "для сервісу рекомендації фільмів. "
    "Відповідай тільки назвою."
)

FACTUAL = (
    "У якому році випустили перший iPhone? "
    "Відповідай лише роком."
)

results = []
OUTPUT = Path("sampling_results_variant9.json")


def run(prompt, experiment, n=5, **params):
    answers = []

    for attempt in range(1, n + 1):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            **params
        )

        answer = (
            response.choices[0].message.content or ""
        ).strip()

        answers.append(answer)

        results.append({
            "experiment": experiment,
            "model": model,
            "prompt": prompt,
            "run": attempt,
            "parameters": params,
            "answer": answer
        })

        OUTPUT.write_text(
            json.dumps(
                results,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print(
            f"{experiment} | "
            f"запуск {attempt}/{n}: {answer}",
            flush=True
        )

    return answers


print("\n=== ВПЛИВ TEMPERATURE ===")

for t in [0.0, 0.7, 1.5]:
    answers = run(
        CREATIVE,
        f"temperature_{t}",
        temperature=t
    )

    print(
        f"Унікальних: {len(set(answers))}/5"
    )


print("\n=== ВПЛИВ TOP_P ===")

for p in [0.1, 0.5, 1.0]:
    answers = run(
        CREATIVE,
        f"top_p_{p}",
        temperature=0.7,
        top_p=p
    )

    print(
        f"Унікальних: {len(set(answers))}/5"
    )


print("\n=== ФАКТИЧНЕ ПИТАННЯ ===")

for t in [0.0, 1.5]:
    answers = run(
        FACTUAL,
        f"factual_{t}",
        temperature=t
    )

    correct = sum(
        answer.strip().strip(".") == "2007"
        for answer in answers
    )

    print(f"Правильних: {correct}/5")


print("\n=== ВІДТВОРЮВАНІСТЬ ===")

answers = run(
    FACTUAL,
    "reproducibility",
    n=10,
    temperature=0.0
)

print(f"Унікальних відповідей: {len(set(answers))}")
print(f"Усі однакові: {len(set(answers)) == 1}")

print("\nГотово!")
print(f"Збережено: {OUTPUT}")
