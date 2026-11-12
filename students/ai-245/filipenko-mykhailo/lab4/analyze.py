import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

import config
from logparse import parse_log
from metrics import calculate_metrics


MODES = ["none", "trim", "trim+state"]


def load_results():
    results = []

    for path in sorted(Path("results").glob("*.json")):
        if path.name in {"analysis.json", "summary.json"}:
            continue

        try:
            with open(path, encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, ValueError):
            continue

        if not isinstance(data, dict):
            continue

        if "run_id" not in data or "mode" not in data:
            continue

        if data["mode"] not in MODES:
            continue

        log_path = Path(data.get("log_path", ""))

        if not log_path.is_file():
            old_path = Path(str(log_path) + ".log")

            if old_path.is_file():
                log_path = old_path
            else:
                print(f"Лог не знайдено: {log_path}")
                continue

        runs = parse_log(log_path)

        valid_runs = [
            run for run in runs
            if run["steps"] > 0
        ]

        if not valid_runs:
            print(f"Немає кроків у логу: {log_path}")
            continue

        run = valid_runs[-1]

        metrics = calculate_metrics(
            run,
            num_ctx=data.get("num_ctx", config.NUM_CTX)
        )

        results.append({
            "run_id": data["run_id"],
            "tag": data.get("tag", ""),
            "mode": data["mode"],
            "repeat": data.get("repeat", 1),
            "num_ctx": data.get("num_ctx", config.NUM_CTX),
            "elapsed_seconds": data.get("elapsed_seconds", 0),
            "correct": data.get("correct", False),
            "steps": metrics["steps"],
            "tool_calls": metrics["tool_calls"],
            "repeated_calls": metrics["repeated_calls"],
            "first_prompt_tokens": metrics["first_prompt_tokens"],
            "total_prompt_tokens": metrics["total_prompt_tokens"],
            "total_completion_tokens": metrics["total_completion_tokens"],
            "max_prompt_tokens": metrics["max_prompt_tokens"],
            "context_usage_percent": metrics["context_usage_percent"],
            "context_growth": metrics["context_growth"],
            "median_delta": metrics["median_delta"],
            "predicted_total_tokens": metrics["predicted_total_tokens"],
            "context_overflow": metrics["context_overflow"],
            "compressions": metrics["compressions"],
            "cache_hits": metrics["cache_hits"],
            "cache_misses": metrics["cache_misses"],
            "has_answer": metrics["has_answer"],
            "stopped": metrics["stopped"]
        })

    return results


def make_summary(results):
    groups = defaultdict(list)

    for item in results:
        key = (
            item["tag"],
            item["mode"],
            item["num_ctx"]
        )
        groups[key].append(item)

    summary = []

    for (tag, mode, num_ctx), items in sorted(groups.items()):
        summary.append({
            "tag": tag,
            "mode": mode,
            "num_ctx": num_ctx,
            "runs": len(items),
            "median_time_seconds": round(
                statistics.median(
                    item["elapsed_seconds"]
                    for item in items
                ),
                2
            ),
            "median_steps": statistics.median(
                item["steps"]
                for item in items
            ),
            "median_tool_calls": statistics.median(
                item["tool_calls"]
                for item in items
            ),
            "median_prompt_tokens": statistics.median(
                item["total_prompt_tokens"]
                for item in items
            ),
            "median_completion_tokens": statistics.median(
                item["total_completion_tokens"]
                for item in items
            ),
            "median_max_prompt_tokens": statistics.median(
                item["max_prompt_tokens"]
                for item in items
            ),
            "median_compressions": statistics.median(
                item["compressions"]
                for item in items
            ),
            "median_repeated_calls": statistics.median(
                item["repeated_calls"]
                for item in items
            ),
            "correct_runs": sum(
                bool(item["correct"])
                for item in items
            )
        })

    return summary


def save_csv(path, rows):
    if not rows:
        return

    with open(
        path,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(rows[0].keys())
        )
        writer.writeheader()
        writer.writerows(rows)


def analyze():
    Path("results").mkdir(exist_ok=True)

    results = load_results()

    if not results:
        print("Немає результатів для аналізу.")
        return

    summary = make_summary(results)

    analysis_json = Path("results/analysis.json")
    analysis_csv = Path("results/analysis.csv")
    summary_json = Path("results/summary.json")
    summary_csv = Path("results/summary.csv")

    with open(
        analysis_json,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            results,
            file,
            ensure_ascii=False,
            indent=2
        )

    with open(
        summary_json,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            summary,
            file,
            ensure_ascii=False,
            indent=2
        )

    save_csv(analysis_csv, results)
    save_csv(summary_csv, summary)

    print("\nАНАЛІЗ ЛР4")
    print("=" * 60)
    print(f"Проаналізовано запусків: {len(results)}")
    print(f"Груп результатів: {len(summary)}")

    for item in summary:
        print()
        print(f"Тег: {item['tag']}")
        print(f"Режим: {item['mode']}")
        print(f"Контекст: {item['num_ctx']}")
        print(f"Запусків: {item['runs']}")
        print(f"Медіана часу: {item['median_time_seconds']} с")
        print(f"Медіана кроків: {item['median_steps']}")
        print(f"Медіана викликів: {item['median_tool_calls']}")
        print(f"Медіана вхідних токенів: {item['median_prompt_tokens']}")
        print(f"Медіана стиснень: {item['median_compressions']}")
        print(f"Правильних запусків: {item['correct_runs']}/{item['runs']}")

    print()
    print(f"Детальний JSON: {analysis_json}")
    print(f"Детальний CSV: {analysis_csv}")
    print(f"Підсумковий JSON: {summary_json}")
    print(f"Підсумковий CSV: {summary_csv}")


if __name__ == "__main__":
    analyze()
