import os
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

# ==========================================
# Лабораторна робота №1
# Підключення хмарної моделі Google Gemini
# ==========================================

BASE_DIR = Path(__file__).parent
ENV_FILE = BASE_DIR / ".env"
OUTPUT_FILE = BASE_DIR / "cloud_results.json"

# Завантаження API-ключа з .env
if ENV_FILE.exists():
    for line in ENV_FILE.read_text(
        encoding="utf-8-sig"
    ).splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)

        if key.strip() == "GEMINI_API_KEY":
            os.environ["GEMINI_API_KEY"] = (
                value.strip().strip('"').strip("'")
            )

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY or API_KEY == "ВСТАВ_СЮДИ_НОВИЙ_КЛЮЧ":
    raise SystemExit(
        "Помилка: додай справжній GEMINI_API_KEY у .env"
    )

# Модель зі списку, отриманого через Gemini API
MODEL = "gemini-3.5-flash-lite"

URL = (
    "https://generativelanguage.googleapis.com/"
    f"v1beta/models/{MODEL}:generateContent"
)

QUESTIONS = [
    "Поясни різницю між функцією і методом у Python. Коротко.",
    (
        "Зонд рухається зі швидкістю 60000 км/год. "
        "Відстань становить 480 мільйонів км. "
        "Скільки повних діб триватиме політ? "
        "Поясни обчислення."
    ),
    (
        "Чим зоря відрізняється від планети? "
        "Відповідай українською мовою."
    )
]


def save_results(results):
    OUTPUT_FILE.write_text(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=4
        ),
        encoding="utf-8"
    )


def ask_gemini(question):
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": question}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "maxOutputTokens": 512
        }
    }

    request = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        },
        method="POST"
    )

    with urllib.request.urlopen(
        request,
        timeout=120
    ) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def main():
    results = []

    print("=" * 55)
    print("ТЕСТУВАННЯ ХМАРНОЇ МОДЕЛІ GOOGLE GEMINI")
    print("Модель:", MODEL)
    print("=" * 55)

    for number, question in enumerate(QUESTIONS, start=1):
        print(f"\nЗавдання {number}")
        print("Запитання:", question)

        start = time.perf_counter()

        try:
            data = ask_gemini(question)
            elapsed = round(
                time.perf_counter() - start, 2
            )

            candidates = data.get("candidates", [])
            answer = ""

            if candidates:
                parts = candidates[0].get(
                    "content", {}
                ).get("parts", [])

                answer = "\n".join(
                    part["text"]
                    for part in parts
                    if "text" in part
                )

            usage = data.get("usageMetadata", {})

            print(
                "Відповідь:",
                answer or "(Порожня відповідь)"
            )
            print(f"Час: {elapsed} секунд")

            result = {
                "model": MODEL,
                "provider": "Google Gemini API",
                "type": "Хмарна модель",
                "task": number,
                "prompt": question,
                "answer": answer,
                "time_seconds": elapsed,
                "input_tokens": usage.get(
                    "promptTokenCount"
                ),
                "output_tokens": usage.get(
                    "candidatesTokenCount"
                ),
                "status": (
                    "success"
                    if answer else "empty_response"
                )
            }

        except urllib.error.HTTPError as error:
            elapsed = round(
                time.perf_counter() - start, 2
            )

            details = error.read().decode(
                "utf-8",
                errors="replace"
            )

            # Приховуємо API-ключ у повідомленні
            details = details.replace(
                API_KEY,
                "[ПРИХОВАНИЙ_КЛЮЧ]"
            )

            print(f"HTTP помилка: {error.code}")
            print("Пояснення Google:")
            print(details[:1500])

            result = {
                "model": MODEL,
                "provider": "Google Gemini API",
                "task": number,
                "prompt": question,
                "status": "error",
                "http_code": error.code,
                "error_details": details[:1500],
                "time_seconds": elapsed
            }

        except Exception as error:
            elapsed = round(
                time.perf_counter() - start, 2
            )

            error_type = type(error).__name__

            print("Помилка підключення:", error_type)

            result = {
                "model": MODEL,
                "provider": "Google Gemini API",
                "task": number,
                "prompt": question,
                "status": "error",
                "error_type": error_type,
                "time_seconds": elapsed
            }

        results.append(result)
        save_results(results)

    print("\n" + "=" * 55)
    print("Тестування завершено!")
    print("Результати:", OUTPUT_FILE.name)

    successes = sum(
        item["status"] == "success"
        for item in results
    )

    print(
        f"Успішних відповідей: {successes}/{len(results)}"
    )
    print("=" * 55)


if __name__ == "__main__":
    main()
