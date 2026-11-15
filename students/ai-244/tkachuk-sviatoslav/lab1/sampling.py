"""Завдання 6: 50 незалежних викликів; збереження ВСІХ відповідей і параметрів."""
import re
from config import ROOT, CREATIVE, FACTUAL
from common import chat, save_json, safe_error
from providers import PROVIDERS, make_client


def run(out=ROOT):
    rows = []
    experiments = []
    for t in (0.0, 0.7, 1.5):
        experiments.append(("creative_temperature", 5, CREATIVE, {"temperature": t, "top_p": 1.0}))
    for p in (0.1, 0.5, 1.0):
        experiments.append(("creative_top_p", 5, CREATIVE, {"temperature": 0.7, "top_p": p}))
    for t in (0.0, 1.5):
        experiments.append(("factual_temperature", 5, FACTUAL, {"temperature": t, "top_p": 1.0}))
    experiments.append(("reproducibility", 10, FACTUAL, {"temperature": 0.0, "top_p": 1.0}))
    for experiment, n, prompt, params in experiments:
        for attempt in range(1, n + 1):
            try:
                client, model = make_client("local")
                with client:
                    row = chat(client, model, prompt, **params)
                if experiment.startswith("factual") or experiment == "reproducibility":
                    row["correct"] = bool(re.fullmatch(r"1887[.\s]*", row["response"].strip()))
            except Exception as exc:
                row = {"status": "error", "error": safe_error(exc), "model": PROVIDERS["local"]["model"]}
            row.update(experiment=experiment, attempt=attempt, parameters=params)
            rows.append(row)
            save_json(out / "sampling_results.json", rows)
            print(f"Завдання 6: {experiment} / {params} / {attempt}: {row['status']}", flush=True)
    return rows


if __name__ == "__main__":
    run()

