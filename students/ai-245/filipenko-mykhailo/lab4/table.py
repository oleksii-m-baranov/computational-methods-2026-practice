
import csv
import json
from pathlib import Path
from statistics import mean

MODES = ["none", "trim", "trim+state"]
RESULTS = Path("results")


def load_results(mode):
    runs = []

    for repeat in range(1, 4):
        path = RESULTS / f"{mode}_{repeat}_compare.json"

        if not path.exists():
            raise FileNotFoundError(f"Відсутній файл: {path}")

        with open(path, encoding="utf-8") as file:
            data = json.load(file)

        if data["mode"] != mode:
            raise ValueError(f"Неправильний режим у {path}")

        if data["repeat"] != repeat:
            raise ValueError(f"Неправильний номер повтору у {path}")

        runs.append(data)

    return runs


def main():
    RESULTS.mkdir(exist_ok=True)
    summary = []

    print()
    print("=" * 85)
    print("ПОРІВНЯННЯ РЕЖИМІВ КЕРУВАННЯ КОНТЕКСТОМ")
    print("=" * 85)

    for mode in MODES:
        runs = load_results(mode)
        times = [run["elapsed_seconds"] for run in runs]
        correct_count = sum(bool(run["correct"]) for run in runs)

        row = {
            "mode": mode,
            "runs": len(runs),
            "time_1": times[0],
            "time_2": times[1],
            "time_3": times[2],
            "mean_seconds": round(mean(times), 2),
            "min_seconds": round(min(times), 2),
            "max_seconds": round(max(times), 2),
            "correct_runs": correct_count,
            "accuracy_percent": round(correct_count / len(runs) * 100, 2),
            "compress": runs[0]["compress"],
            "use_state": runs[0].get("use_state", False),
            "expected_total": runs[0]["expected_total"]
        }

        summary.append(row)

        print(f"\nРежим: {mode}")
        print(f"Повторів: {row['runs']}")
        print(f"Час: {times}")
        print(f"Середній час: {row['mean_seconds']} с")
        print(f"Правильність: {correct_count}/{len(runs)}")
        print(f"Стиснення: {row['compress']}")
        print(f"Стан: {row['use_state']}")

    json_path = RESULTS / "comparison.json"
    csv_path = RESULTS / "comparison.csv"

    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(summary[0].keys())
        )
        writer.writeheader()
        writer.writerows(summary)

    baseline = summary[0]["mean_seconds"]

    print()
    print("=" * 85)
    print("ПІДСУМОК")
    print("=" * 85)

    for row in summary:
        difference = round(
            (row["mean_seconds"] - baseline) / baseline * 100,
            2
        )

        print(
            f"{row['mode']:<12} "
            f"середній час={row['mean_seconds']:.2f} с | "
            f"правильність={row['accuracy_percent']:.0f}% | "
            f"різниця часу={difference:+.2f}%"
        )

    print()
    print(f"JSON: {json_path}")
    print(f"CSV: {csv_path}")


if __name__ == "__main__":
    main()
