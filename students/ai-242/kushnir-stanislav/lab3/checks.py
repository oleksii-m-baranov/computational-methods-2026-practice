"""Перевірки змісту аргументів."""
import csv
import difflib

# довідник: ключ, за яким laptop_info шукає рядок (data/laptops.csv, колонка model)
with open("data/laptops.csv", encoding="utf-8") as f:
    VALUES_0 = [row["model"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    """Повертає текст помилки для моделі або None, якщо все гаразд."""
    if name == "laptop_info":
        if args.model.lower() not in [v.lower() for v in VALUES_0]:
            # допустимих значень більше 10 — усі не перелічуємо, а підказуємо схожі за написанням
            if len(VALUES_0) <= 10:
                hint = " Доступні: " + ", ".join(VALUES_0) + "."
            else:
                similar = difflib.get_close_matches(args.model.lower(), [v.lower() for v in VALUES_0], n=3, cutoff=0.6)
                hint = (" Схожі назви в довіднику: " + ", ".join(similar) + ".") if similar else ""
            return (f"Помилка: моделі '{args.model}' немає в довіднику.{hint} "
                    "Назва має бути точною назвою моделі, як у довіднику (наприклад, «LearnPad 14»). Модель могла бути в каталозі search_laptops, але відсутня в довіднику цін. Виправ значення або повідом користувачу, що даних про це немає.")
    return None
