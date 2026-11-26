"""Перевірки змісту аргументів."""
import csv
import difflib

# довідник: ключ, за яким tariff_info шукає рядок (data/tariffs.csv, колонка city)
with open("data/tariffs.csv", encoding="utf-8") as f:
    VALUES_0 = [row["city"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    """Повертає текст помилки для моделі або None, якщо все гаразд."""
    if name == "tariff_info":
        if args.city.lower() not in [v.lower() for v in VALUES_0]:
            # допустимих значень більше 10 — усі не перелічуємо, а підказуємо схожі за написанням
            if len(VALUES_0) <= 10:
                hint = " Доступні: " + ", ".join(VALUES_0) + "."
            else:
                similar = difflib.get_close_matches(args.city.lower(), [v.lower() for v in VALUES_0], n=3, cutoff=0.6)
                hint = (" Схожі назви в довіднику: " + ", ".join(similar) + ".") if similar else ""
            return (f"Помилка: міста '{args.city}' немає в довіднику.{hint} "
                    "Назва має бути в називному відмінку однини (наприклад, «Львів», а не «до Львова»). Виправ значення або повідом користувачу, що даних про це немає.")
    return None
