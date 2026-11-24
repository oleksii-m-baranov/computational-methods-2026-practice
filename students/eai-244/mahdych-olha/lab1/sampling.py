from providers import make_client
import json
from utils.lab_logger import custom_logger

logger = custom_logger("lab1")

client, model = make_client("local")

CREATIVE = "Придумай назву застосунку нагадувань про ліки."
FACTUAL = "У якому році було відкрито Київський метрополітен?"

def run(prompt, n=5, **params):
    answers = []

    for i in range(n):
        print(f"    {i + 1}/{n}", flush=True)

        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **params,
        )

        answers.append(r.choices[0].message.content.strip())

    return answers


experiments = [
    ("temperature_0.0", {"temperature": 0.0}),
    ("temperature_0.7", {"temperature": 0.7}),
    ("temperature_1.5", {"temperature": 1.5}),
    ("top_p_0.1", {"temperature": 0.7, "top_p": 0.1}),
    ("top_p_0.5", {"temperature": 0.7, "top_p": 0.5}),
    ("top_p_1.0", {"temperature": 0.7, "top_p": 1.0}),
]

results = {}

for name, params in experiments:
    print(f"\n=== {name} ===", flush=True)

    print("  creative", flush=True)
    creative = run(CREATIVE, 5, **params)

    print("  factual", flush=True)
    factual = run(FACTUAL, 5, **params)

    results[name] = {
        "creative": creative,
        "factual": factual
    }

    with open("sampling_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"Sampling experiment: {name} — готово")


repeat = run(CREATIVE, 10, temperature=0.0)
results["reproducibility"] = repeat

with open("sampling_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

logger.info("Sampling completed")