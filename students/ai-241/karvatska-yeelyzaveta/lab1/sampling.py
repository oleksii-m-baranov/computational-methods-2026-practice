import json
import time
import requests


OLLAMA_URL = "http://localhost:11434/api/generate"

MODELS = {
    "llama": "llama3.2:3b",
    "qwen": "qwen3:4b",
}

FACT_PROMPT = "Столиця України? Відповідай одним словом."

REASONING_PROMPT = (
    "Ручка і зошит разом коштують 110 грн. "
    "Ручка на 100 грн дешевша за зошит. "
    "Скільки коштує ручка?"
)


def generate(model, prompt):
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.0,
        "top_p": 1.0,
    }

    for attempt in range(2):
        start = time.perf_counter()

        try:
            response = requests.post(
                OLLAMA_URL,
                json=data,
                timeout=300
            )

            elapsed = time.perf_counter() - start

            if response.status_code == 200:
                result = response.json()
                result["_wall_time"] = elapsed
                return result

            print(f"Помилка Ollama: HTTP {response.status_code}")

        except requests.RequestException as error:
            elapsed = time.perf_counter() - start
            print(f"Помилка запиту: {error}")

        if attempt == 0:
            print("Повторюємо запит через 3 секунди...")
            time.sleep(3)

    return {
        "error": "Запит не виконано",
        "_wall_time": elapsed,
    }


def warmup(model):
    print(f"Розігрів моделі {model}...")
    generate(model, "Привіт")


def main():
    results = {}

    for name, model in MODELS.items():
        print()
        print("=" * 60)
        print(f"МОДЕЛЬ: {model}")
        print("=" * 60)

        warmup(model)

        print("\nФактичне питання...")
        fact = generate(model, FACT_PROMPT)

        print("Відповідь:", repr(fact.get("response")))
        print("eval_count:", fact.get("eval_count"))
        print("total_duration:", fact.get("total_duration"))
        print("eval_duration:", fact.get("eval_duration"))
        print("done_reason:", fact.get("done_reason"))

        print("\nЗадача на міркування — 5 запусків...")

        reasoning_runs = []

        for i in range(5):
            print(f"Запуск {i + 1}/5...")

            result = generate(model, REASONING_PROMPT)

            reasoning_runs.append({
                "run": i + 1,
                "response": result.get("response"),
                "thinking": result.get("thinking"),
                "eval_count": result.get("eval_count"),
                "total_duration": result.get("total_duration"),
                "eval_duration": result.get("eval_duration"),
                "prompt_eval_count": result.get("prompt_eval_count"),
                "prompt_eval_duration": result.get("prompt_eval_duration"),
                "load_duration": result.get("load_duration"),
                "done_reason": result.get("done_reason"),
                "wall_time": result.get("_wall_time"),
                "error": result.get("error"),
            })

            print("Відповідь:", repr(result.get("response")))

        results[name] = {
            "model": model,
            "fact": {
                "prompt": FACT_PROMPT,
                "response": fact.get("response"),
                "eval_count": fact.get("eval_count"),
                "total_duration": fact.get("total_duration"),
                "eval_duration": fact.get("eval_duration"),
                "prompt_eval_count": fact.get("prompt_eval_count"),
                "prompt_eval_duration": fact.get("prompt_eval_duration"),
                "load_duration": fact.get("load_duration"),
                "done_reason": fact.get("done_reason"),
                "wall_time": fact.get("_wall_time"),
            },
            "reasoning": {
                "prompt": REASONING_PROMPT,
                "runs": reasoning_runs,
            },
        }

    with open(
        "lab1_results.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 60)
    print("ГОТОВО")
    print("Результати збережено у lab1_results.json")
    print("=" * 60)


if __name__ == "__main__":
    main()