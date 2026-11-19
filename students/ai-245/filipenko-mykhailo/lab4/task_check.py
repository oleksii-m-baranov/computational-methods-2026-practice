
import csv
import json
import sys
from pathlib import Path

from logparse import parse_log


def load_models():
    with open("long_task.json", encoding="utf-8") as file:
        task = json.load(file)

    return [
        item["model"]
        for item in task["expected"]["details"]
    ]


def load_prices():
    with open(
        "data/laptops.csv",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        return {
            row["model"]: float(row["price"])
            for row in csv.DictReader(file)
        }


def check_task(log_path):
    runs = parse_log(log_path)
    runs = [run for run in runs if run["steps"] > 0]

    if not runs:
        print("У логу немає завершених кроків агента.")
        return

    run = runs[-1]
    models = load_models()
    prices = load_prices()
    calls = run["tool_details"]

    print("ПЕРЕВІРКА ДОВГОЇ ЗАДАЧІ")
    print("=" * 60)

    completed = 0

    for model in models:
        search_found = False
        info_found = False
        installment_found = False

        for call in calls:
            try:
                args = json.loads(call["arguments"])
            except (ValueError, TypeError):
                continue

            name = call["name"]

            if (
                name == "search_laptops"
                and args.get("query", "").strip().lower()
                == model.lower()
            ):
                search_found = True

            if (
                name == "laptop_info"
                and args.get("model", "").strip().lower()
                == model.lower()
            ):
                info_found = True

            if name == "calc_installment":
                if (
                    float(args.get("price", -1)) == prices[model]
                    and float(args.get("months", -1)) == 12
                    and float(args.get("overpay_percent", -1)) == 10
                ):
                    installment_found = True

        complete = (
            search_found
            and info_found
            and installment_found
        )

        if complete:
            completed += 1

        print()
        print(model)
        print(f"  Пошук: {search_found}")
        print(f"  Інформація: {info_found}")
        print(f"  Розстрочка: {installment_found}")
        print(f"  Повністю: {complete}")

    print()
    print("=" * 60)
    print(f"Оброблено моделей: {completed}/{len(models)}")
    print(f"Усього викликів: {run['tool_calls']}")
    print(f"Мінімум викликів: 18")
    print(
        "Усі моделі перевірені:",
        completed == len(models)
    )


if __name__ == "__main__":
    path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "logs/test3072_trim_r1.log"
    )

    check_task(Path(path))
