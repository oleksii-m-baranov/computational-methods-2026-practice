import csv
import json
import re
from pathlib import Path
from statistics import median

MODES = ["none", "trim", "trim+state"]
RESULTS = Path("results")
LOGS = Path("logs")

# Команда: python measure.py all 3 main
RUN_TAG = "main"
REPEATS = 3


def result_path(mode, repeat):
    return RESULTS / f"{RUN_TAG}_{mode}_r{repeat}.json"


def log_path(mode, repeat):
    return LOGS / f"{RUN_TAG}_{mode}_r{repeat}.log"


def extract_numbers(pattern, text):
    return [
        int(value)
        for value in re.findall(pattern, text)
    ]


def parse_log(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Відсутній журнал: {path}"
        )

    text = path.read_text(encoding="utf-8-sig")

    prompt_tokens = extract_numbers(
        r"prompt_tokens=(\d+)", text
    )
    completion_tokens = extract_numbers(
        r"completion_tokens=(\d+)", text
    )

    steps = len(
        re.findall(r"--- крок \d+ \|", text)
    )

    compressions = len(
        re.findall(r"СТИСНЕННЯ:", text)
    )

    hits = len(
        re.findall(r"КЕШ:\s*HIT", text)
    )

    misses = len(
        re.findall(r"КЕШ:\s*MISS", text)
    )

    calls = re.findall(
        r"виклик\s*:\s*(\w+)\((.*)\)",
        text
    )

    seen = set()
    repeated_calls = 0

    for name, args_text in calls:
        try:
            args = json.loads(args_text)
            normalized = json.dumps(
                args,
                sort_keys=True,
                ensure_ascii=False
            )
        except (ValueError, TypeError):
            normalized = args_text.strip()

        key = (name, normalized)

        if key in seen:
            repeated_calls += 1
        else:
            seen.add(key)

    return {
        "steps": steps,
        "prompt_tokens": sum(prompt_tokens),
        "completion_tokens": sum(
            completion_tokens
        ),
        "total_tokens": (
            sum(prompt_tokens)
            + sum(completion_tokens)
        ),
        "max_prompt_tokens": (
            max(prompt_tokens)
            if prompt_tokens else 0
        ),
        "compressions": compressions,
        "repeated_calls": repeated_calls,
        "cache_hits": hits,
        "cache_misses": misses
    }


def load_run(mode, repeat):
    path = result_path(mode, repeat)

    if not path.exists():
        raise FileNotFoundError(
            f"Відсутній результат: {path}"
        )

    with open(path, encoding="utf-8") as file:
        data = json.load(file)

    if data.get("mode") != mode:
        raise ValueError(
            f"Неправильний режим у {path}"
        )

    elapsed = data.get(
        "elapsed_seconds",
        data.get("elapsed")
    )

    if elapsed is None:
        raise ValueError(
            f"Не знайдено часу виконання у {path}. "
            f"Доступні поля: {list(data.keys())}"
        )

    metrics = parse_log(
        log_path(mode, repeat)
    )

    return {
        "mode": mode,
        "repeat": repeat,
        "elapsed_seconds": float(elapsed),
        "correct": bool(data.get("correct", False)),
        **metrics
    }


def med(runs, field):
    return round(
        median(run[field] for run in runs),
        2
    )


def summarize(mode, runs):
    correct_count = sum(
        1 for run in runs if run["correct"]
    )

    return {
        "mode": mode,
        "runs": len(runs),
        "median_steps": med(runs, "steps"),
        "median_prompt_tokens": med(
            runs, "prompt_tokens"
        ),
        "median_completion_tokens": med(
            runs, "completion_tokens"
        ),
        "median_total_tokens": med(
            runs, "total_tokens"
        ),
        "median_max_prompt_tokens": med(
            runs, "max_prompt_tokens"
        ),
        "median_seconds": med(
            runs, "elapsed_seconds"
        ),
        "median_compressions": med(
            runs, "compressions"
        ),
        "median_repeated_calls": med(
            runs, "repeated_calls"
        ),
        "correct_runs": correct_count,
        "accuracy_percent": round(
            correct_count / len(runs) * 100,
            2
        )
    }


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


def main():
    RESULTS.mkdir(
        parents=True,
        exist_ok=True
    )

    summaries = []
    all_runs = []

    print()
    print("=" * 90)
    print("ТАБЛИЦЯ 5 — ПОРІВНЯННЯ РЕЖИМІВ")
    print("=" * 90)

    for mode in MODES:
        runs = [
            load_run(mode, repeat)
            for repeat in range(1, REPEATS + 1)
        ]

        all_runs.extend(runs)

        summary = summarize(mode, runs)
        summaries.append(summary)

        print()
        print(f"Режим: {mode}")
        print(f"Повторів: {summary['runs']}")

        print(
            "Медіана кроків: "
            f"{summary['median_steps']}"
        )
        print(
            "Медіана вхідних токенів: "
            f"{summary['median_prompt_tokens']}"
        )
        print(
            "Медіана вихідних токенів: "
            f"{summary['median_completion_tokens']}"
        )
        print(
            "Медіана всіх токенів: "
            f"{summary['median_total_tokens']}"
        )
        print(
            "Медіана максимального входу: "
            f"{summary['median_max_prompt_tokens']}"
        )
        print(
            "Медіана часу: "
            f"{summary['median_seconds']} с"
        )
        print(
            "Медіана стискань: "
            f"{summary['median_compressions']}"
        )
        print(
            "Медіана повторних викликів: "
            f"{summary['median_repeated_calls']}"
        )
        print(
            "Правильних запусків: "
            f"{summary['correct_runs']}/{summary['runs']}"
        )

    json_path = RESULTS / "comparison.json"
    csv_path = RESULTS / "comparison.csv"
    runs_path = RESULTS / "comparison_runs.csv"

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            summaries,
            file,
            ensure_ascii=False,
            indent=2
        )

    save_csv(csv_path, summaries)
    save_csv(runs_path, all_runs)

    baseline = summaries[0]["median_seconds"]

    print()
    print("=" * 90)
    print("ПІДСУМОК")
    print("=" * 90)

    for row in summaries:
        current = row["median_seconds"]

        if baseline > 0:
            difference = (
                (current - baseline)
                / baseline * 100
            )
            difference_text = (
                f"{difference:+.2f}%"
            )
        else:
            difference_text = "неможливо обчислити"

        print(
            f"{row['mode']:<12} | "
            f"медіана часу: {current:.2f} с | "
            f"правильність: "
            f"{row['correct_runs']}/{row['runs']} | "
            f"зміна часу: {difference_text}"
        )

    print()
    print(f"JSON: {json_path}")
    print(f"CSV: {csv_path}")
    print(f"Окремі запуски: {runs_path}")


if __name__ == "__main__":
    main()
