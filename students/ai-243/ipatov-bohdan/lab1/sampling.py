import json
from providers import make_client

client, model = make_client("local")

CREATIVE = "Назва стартапу в галузі логістики"
FACTUAL = "Рік заснування Національного університету \"Одеська Політехніка\""


def run(prompt: str, n: int = 5, **params):
    """Execute prompt n times with given inference parameters and return list of responses."""
    answers = []
    for _ in range(n):
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **params,
        )
        answers.append(r.choices[0].message.content.strip())
    return answers


results = {
    "temperature_creative": {},
    "top_p_creative": {},
    "temperature_factual": {},
    "determinism": {},
}

print("=== Impact of temperature on creativity ===")
for t in [0.0, 0.7, 1.5]:
    answers = run(CREATIVE, temperature=t)
    unique_count = len(set(answers))
    results["temperature_creative"][str(t)] = {
        "unique": unique_count,
        "answers": answers,
    }
    print(f"temperature={t}: unique {unique_count} of 5")
    for a in answers:
        print(f"  {a}")

print("\n=== Impact of top_p on creativity ===")
for p in [0.1, 0.5, 1.0]:
    answers = run(CREATIVE, temperature=0.7, top_p=p)
    unique_count = len(set(answers))
    results["top_p_creative"][str(p)] = {
        "unique": unique_count,
        "answers": answers,
    }
    print(f"top_p={p}: unique {unique_count} of 5")
    for a in answers:
        print(f"  {a}")

print("\n=== Impact of temperature on factual accuracy ===")
for t in [0.0, 1.5]:
    answers = run(FACTUAL, temperature=t)
    correct_count = sum(1 for a in answers if "1918" in a)
    results["temperature_factual"][str(t)] = {
        "correct": correct_count,
        "answers": answers,
    }
    print(f"temperature={t}: correct {correct_count}/5, answers: {answers}")

print("\n=== Determinism check (10 runs at temperature=0.0) ===")
answers = run(FACTUAL, n=10, temperature=0.0)
unique_count = len(set(answers))
all_identical = unique_count == 1
results["determinism"] = {
    "runs": 10,
    "temperature": 0.0,
    "unique_count": unique_count,
    "all_identical": all_identical,
    "answers": answers,
}
print(f"All answers identical: {all_identical} (unique: {unique_count})")

with open("sampling_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\nSaved sampling_results.json")
