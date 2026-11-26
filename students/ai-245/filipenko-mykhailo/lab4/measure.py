import argparse
import json
import re
import time
from pathlib import Path

from langfuse import get_client, propagate_attributes

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

    normalized = normalize_number(answer)
    expected_text = normalize_number(f"{expected:.2f}")

    return expected_text in normalized


def result_is_complete(result_path, log_path, run_id):
    if not result_path.exists() or not log_path.exists():
        return False

    try:
        with open(result_path, encoding="utf-8") as file:
            data = json.load(file)

        return (
            isinstance(data, dict)
            and data.get("run_id") == run_id
            and "elapsed_seconds" in data
            and "correct" in data
        )
    except (OSError, ValueError, TypeError):
        return False


def save_result(result_path, result):
    temp_path = result_path.with_suffix(".json.tmp")

    with open(temp_path, "w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=2
        )

    temp_path.replace(result_path)


def main():
    parser = argparse.ArgumentParser(
        description="Вимірювання роботи агента"
    )

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

    parser.add_argument(
        "--force",
        action="store_true",
        help="Повторно виконати вже завершені запуски"
    )

    args = parser.parse_args()

    if args.repeats < 1:
        parser.error(
            "Кількість повторів має бути більшою за нуль"
        )

    task = load_task()
    expected = get_expected(task)

    langfuse = get_client()

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

    total_runs = len(modes) * args.repeats
    completed = 0
    skipped = 0
    failed = 0

    print("\n" + "=" * 60)
    print("ЗАПУСК ЕКСПЕРИМЕНТІВ")
    print("=" * 60)
    print(f"Модель: {config.MODEL}")
    print(f"Контекст: {config.NUM_CTX}")
    print(f"Режими: {', '.join(modes)}")
    print(f"Повторів на режим: {args.repeats}")
    print(f"Заплановано запусків: {total_runs}")
    print(f"Кеш: {config.USE_CACHE}")
    print(f"Примусовий повтор: {args.force}")
    print("=" * 60)

    for mode in modes:
        config.COMPRESS = (
            "trim" if mode != "none" else "none"
        )

        config.USE_STATE = mode == "trim+state"

        for repeat in range(1, args.repeats + 1):
            run_id = f"{args.tag}_{mode}_r{repeat}"

            trace_name = (
                run_id
                if run_id.startswith("long-")
                else f"long-{run_id}"
            )

            log_path = (
                Path("logs") / f"{run_id}.log"
            )

            result_path = (
                Path("results") / f"{run_id}.json"
            )

            if not args.force and result_is_complete(
                result_path,
                log_path,
                run_id
            ):
                skipped += 1

                print(
                    f"\nПРОПУЩЕНО: {run_id} "
                    "(результат уже існує)"
                )

                continue

            print("\n" + "-" * 60)
            print(f"ПОЧАТОК: {run_id}")
            print(f"Langfuse trace: {trace_name}")
            print(f"Режим: {mode}")
            print(f"Стиснення: {config.COMPRESS}")
            print(f"Збереження стану: {config.USE_STATE}")
            print(f"Кеш: {config.USE_CACHE}")
            print("-" * 60)

            started = time.perf_counter()

            try:
                with langfuse.start_as_current_observation(
                    as_type="span",
                    name=trace_name
                ) as root_span:

                    with propagate_attributes(
                        trace_name=trace_name,
                        tags=["lab4", args.tag, mode]
                    ):
                        root_span.update(
                            input=task["question"],
                            metadata={
                                "run_id": run_id,
                                "mode": mode,
                                "model": config.MODEL,
                                "num_ctx": config.NUM_CTX,
                                "compress": config.COMPRESS,
                                "use_state": config.USE_STATE,
                                "use_cache": config.USE_CACHE,
                                "repeat": repeat
                            }
                        )

                        answer = run_agent(
                            task["question"],
                            max_steps=config.MAX_STEPS_LONG,
                            logfile_name=str(
                                log_path.with_suffix("")
                            ),
                            task_id=run_id,
                            log_overwrite=True,
                            task_data=task
                        )

                        root_span.update(output=answer)

            except KeyboardInterrupt:
                print(
                    f"\nЗУПИНЕНО КОРИСТУВАЧЕМ: {run_id}"
                )
                print(
                    "Попередні завершені результати "
                    "збережено."
                )
                langfuse.flush()
                raise SystemExit(130)

            except Exception as error:
                failed += 1

                print(
                    f"\nПОМИЛКА ЗАПУСКУ {run_id}: "
                    f"{type(error).__name__}: {error}"
                )

                print(
                    "Результат не записано. "
                    "Цей запуск можна повторити."
                )

                langfuse.flush()
                continue

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
                "trace_name": trace_name,
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

            save_result(
                result_path,
                result
            )

            completed += 1

            langfuse.flush()

            print("\n" + "=" * 60)
            print(f"ЗАВЕРШЕНО: {run_id}")
            print(f"Langfuse trace: {trace_name}")
            print(f"Режим: {mode}")
            print(f"Стиснення: {config.COMPRESS}")
            print(f"Збереження стану: {config.USE_STATE}")
            print(f"Кеш: {config.USE_CACHE}")
            print(f"Час: {elapsed} с")
            print(
                f"Очікувана сума: "
                f"{expected:.2f} грн"
            )
            print(f"Правильність відповіді: {correct}")
            print(f"Лог: {log_path}")
            print(f"Результат: {result_path}")
            print("=" * 60)

    langfuse.flush()

    print("\n" + "=" * 60)
    print("ПІДСУМОК ЕКСПЕРИМЕНТІВ")
    print("=" * 60)
    print(f"Заплановано: {total_runs}")
    print(f"Пропущено готових: {skipped}")
    print(f"Нових завершених: {completed}")
    print(f"Помилок запуску: {failed}")
    print("=" * 60)

    if failed:
        print(
            "Увага: частина запусків не завершилася. "
            "Їх можна повторити тією самою командою."
        )


if __name__ == "__main__":
    main()
