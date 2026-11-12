import argparse
import json
import re
import time
from pathlib import Path

import config
from agent import run_agent


def load_task():
    with open("long_task.json", encoding="utf-8") as file:
        return json.load(file)


def get_expected(task):
    expected = task["expected"]

    if isinstance(expected, dict):
        return float(expected["total_monthly_payment"])

    return float(str(expected).replace(",", "."))


def normalize_number(text):
    return re.sub(r"\s+", "", str(text)).replace(",", ".")


def check_answer(answer, expected, task=None):
    if not answer:
        return False

    text = str(answer)
    normalized = normalize_number(text)

    if normalize_number(f"{expected:.2f}") not in normalized:
        return False

    if task is None:
        return True

    details = task.get("expected", {}).get("details", [])

    for item in details:
        model = item["model"]

        if model not in text:
            return False

        price = float(item["price"])
        months = int(task["months"])
        overpay = float(task["overpay_percent"])

        monthly = round(
            price * (1 + overpay / 100) / months,
            2
        )

        if normalize_number(f"{monthly:.2f}") not in normalized:
            return False

    return True


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "mode",
        choices=["none", "trim", "trim+state", "all"]
    )

    parser.add_argument(
        "repeats",
        type=int
    )

    parser.add_argument(
        "tag",
        nargs="?",
        default="main"
    )

    args = parser.parse_args()

    if args.repeats < 1:
        parser.error(
            "Кількість повторів має бути більшою за нуль"
        )

    task = load_task()
    expected = get_expected(task)

    Path("logs").mkdir(
        parents=True,
        exist_ok=True
    )

    Path("results").mkdir(
        parents=True,
        exist_ok=True
    )

    modes = (
        ["none", "trim", "trim+state"]
        if args.mode == "all"
        else [args.mode]
    )

    config.USE_CACHE = args.tag.startswith("cache")

    for mode in modes:
        config.COMPRESS = (
            "trim" if mode != "none" else "none"
        )

        config.USE_STATE = mode == "trim+state"

        for repeat in range(1, args.repeats + 1):
            run_id = f"{args.tag}_{mode}_r{repeat}"

            log_path = (
                Path("logs") / f"{run_id}.log"
            )

            result_path = (
                Path("results") / f"{run_id}.json"
            )

            started = time.perf_counter()

            answer = run_agent(
                task["question"],
                max_steps=config.MAX_STEPS_LONG,
                logfile_name=str(log_path.with_suffix("")),
                task_id=run_id,
                log_overwrite=True,
                task_data=task
            )

            elapsed = round(
                time.perf_counter() - started,
                2
            )

            correct = check_answer(
                answer,
                expected,
                task
            )

            result = {
                "run_id": run_id,
                "mode": mode,
                "repeat": repeat,
                "tag": args.tag,
                "model": config.MODEL,
                "num_ctx": config.NUM_CTX,
                "compress": config.COMPRESS,
                "use_state": config.USE_STATE,
                "use_cache": config.USE_CACHE,
                "elapsed_seconds": elapsed,
                "expected_total": expected,
                "answer": answer,
                "correct": correct,
                "min_calls": task["min_calls"],
                "log_path": str(log_path)
            }

            with open(
                result_path,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    result,
                    file,
                    ensure_ascii=False,
                    indent=2
                )

            print("\n" + "=" * 60)
            print(f"Запуск: {run_id}")
            print(f"Режим: {mode}")
            print(f"Стиснення: {config.COMPRESS}")
            print(f"Збереження стану: {config.USE_STATE}")
            print(f"Кеш: {config.USE_CACHE}")
            print(f"Час: {elapsed} с")
            print(
                f"Очікувана сума: {expected:.2f} грн"
            )
            print(f"Правильність відповіді: {correct}")
            print(f"Лог: {log_path}")
            print(f"Результат: {result_path}")
            print("=" * 60)


if __name__ == "__main__":
    main()
