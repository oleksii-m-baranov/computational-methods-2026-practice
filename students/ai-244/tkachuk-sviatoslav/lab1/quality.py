"""Завдання 5: 6 умов × 2 повтори × 3 моделі. Зберігає повні відповіді."""
from config import ROOT, TASKS, QUALITY_PROVIDERS
from common import chat, save_json, safe_error
from providers import PROVIDERS, make_client


def run(out=ROOT):
    result, meta = {}, []
    for provider in QUALITY_PROVIDERS:
        model = PROVIDERS[provider]["model"]
        if model in result:
            raise ValueError("Для quality.json оберіть різні назви моделей у .env.")
        result[model] = {}
        for task, prompt in TASKS.items():
            result[model][task] = []
            for attempt in range(1, 3):
                try:
                    client, model = make_client(provider)
                    with client:
                        row = chat(client, model, prompt)
                    # Обриви не можна оцінювати як повноцінну відповідь.
                    answer = row["response"] if row["status"] == "ok" else None
                except Exception as exc:
                    answer = None
                    row = {"status": "error", "error": safe_error(exc)}
                row.update(provider=provider, model=model, task=task, attempt=attempt)
                result[model][task].append(answer)
                meta.append(row)
                save_json(out / "quality.json", result)
                save_json(out / "quality_meta.json", meta)
                print(f"Завдання 5: {model} / {task} / {attempt}: {row['status']}", flush=True)
    return result


if __name__ == "__main__":
    run()

