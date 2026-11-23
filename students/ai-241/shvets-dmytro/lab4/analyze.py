
"""Аналіз одного журналу запуску."""
import sys
import config
from logparse import parse_log
from metrics import describe


def main():
    if len(sys.argv) < 2:
        print("Використання: python analyze.py logs\\назва.log")
        return

    with open(sys.argv[1], encoding="utf-8") as f:
        runs = parse_log(f.read())

    if not runs:
        print("У файлі не знайдено запусків агента.")
        return

    for run in runs:
        d = describe(run)

        print("\n=== АНАЛІЗ ПРОГОНУ ===")
        print("Статус:", d["status"])
        print("Кроків:", d["steps"])
        print("Викликів інструментів:", d["calls"])
        print("Повторних викликів:", d["repeats"])
        print("Перший вхід:", d["first_tokens"])
        print("Типовий приріст:", d["typical_growth"])
        print("Найбільший вхід:", d["max_tokens"])
        print("Розмір вікна:", config.NUM_CTX)
        print("Сума prompt_tokens:", d["prompt_tokens"])
        print("Сума completion_tokens:", d["completion_tokens"])
        print("За формулою:", round(d["formula"]))
        print("Крок застою:", d["stall"])
        print("Влучань у кеш:", d["cache_hits"])

        for number, data in d["squeezes"]:
            print(
                f"Стиснення на кроці {number}: "
                f"{data[0]} токенів, "
                f"{data[1]} -> {data[2]} повідомлень"
            )

        if len(sys.argv) > 2 and sys.argv[2] == "steps":
            print("\nКрок | Вхід | Приріст | Виклики")
            previous = None
            for s in run["steps"]:
                t = s["tokens"]
                diff = t - previous if (
                    t is not None and previous is not None
                ) else "-"
                print(
                    f"{s['n']} | {t} | {diff} | "
                    f"{len(s['calls'])}"
                )
                if t is not None:
                    previous = t


if __name__ == "__main__":
    main()
