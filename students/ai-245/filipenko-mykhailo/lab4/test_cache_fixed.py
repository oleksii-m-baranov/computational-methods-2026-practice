
import json
import tempfile
from pathlib import Path

import cache
import config

from model import call_model
from utils.lab_logger import custom_logger


RESULTS_DIR = Path("results")
LOGS_DIR = Path("logs")

RESULTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Увімкнути кешування
config.USE_CACHE = True

# Три фіксовані запити
QUESTIONS = [
    "Знайди інформацію про ноутбук StudyNova 14.",
    "Знайди інформацію про ноутбук CodeNova 15.",
    "Знайди інформацію про ноутбук GameNova X16."
]

SYSTEM_PROMPT = (
    "Ти консультант магазину ноутбуків. "
    "Відповідай українською мовою. "
    "Не вигадуй інформацію."
)


def run_test(name, logger):
    hits = 0
    misses = 0
    results = []

    print("\n" + "=" * 55)
    print(f"ЗАПУСК: {name}")
    print("=" * 55)

    for index, question in enumerate(QUESTIONS, start=1):
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": question
            }
        ]

        response, from_cache = call_model(
            messages,
            index,
            logger
        )

        if response is None:
            raise RuntimeError(
                f"Модель не відповіла на запит {index}"
            )

        status = "HIT" if from_cache else "MISS"

        if from_cache:
            hits += 1
        else:
            misses += 1

        print(f"Запит {index}: {status}")

        results.append({
            "question": question,
            "cache": status,
            "response": response.model_dump(
                mode="json"
            )
        })

    print()
    print(f"HIT: {hits}/3")
    print(f"MISS: {misses}/3")

    return {
        "name": name,
        "hits": hits,
        "misses": misses,
        "results": results
    }


def main():
    # Створюємо нову унікальну папку.
    # Нічого не видаляємо.
    test_cache_dir = Path(
        tempfile.mkdtemp(
            prefix="lab4_cache_test_"
        )
    )

    # cache.ask_model використовує
    # саме цю змінну.
    cache.CACHE_DIR = test_cache_dir

    print("Тестовий кеш:", test_cache_dir)
    print("Початковий стан: порожній кеш")

    logger = custom_logger(
        "cache_fixed.log",
        overwrite=True
    )

    # Перший запуск: порожній кеш
    cold = run_test(
        "COLD CACHE",
        logger
    )

    # Другий запуск: той самий кеш
    # і точно такі самі запити
    warm = run_test(
        "WARM CACHE",
        logger
    )

    report = {
        "cache_directory": str(test_cache_dir),
        "cold": cold,
        "warm": warm
    }

    output = RESULTS_DIR / "cache_fixed.json"

    with open(
        output,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\n" + "=" * 55)
    print("ПІДСУМКИ ЕКСПЕРИМЕНТУ")
    print("=" * 55)

    print(
        f"COLD: HIT={cold['hits']}, "
        f"MISS={cold['misses']}"
    )

    print(
        f"WARM: HIT={warm['hits']}, "
        f"MISS={warm['misses']}"
    )

    # Перевірка холодного кешу
    assert cold["hits"] == 0, (
        "Помилка: холодний кеш має HIT"
    )

    assert cold["misses"] == 3, (
        "Помилка: очікувалося 3 MISS"
    )

    # Перевірка теплого кешу
    assert warm["hits"] == 3, (
        "Помилка: очікувалося 3 HIT"
    )

    assert warm["misses"] == 0, (
        "Помилка: теплий кеш має MISS"
    )

    # Перевірка однакових відповідей
    for first, second in zip(
        cold["results"],
        warm["results"]
    ):
        assert (
            first["response"]
            == second["response"]
        ), "Відповіді кешу відрізняються"

    print()
    print("CACHE TEST: PASS")
    print(f"Результати: {output}")
    print(f"Лог: {LOGS_DIR / 'cache_fixed.log'}")


if __name__ == "__main__":
    main()
