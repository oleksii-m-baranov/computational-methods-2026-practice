"""Перевірки змісту аргументів."""
import csv
import difflib

# довідник: ключ, за яким price_info шукає рядок (data/prices.csv, колонка service)
with open("data/prices.csv", encoding="utf-8") as f:
    VALUES_0 = [row["service"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    """Повертає текст помилки для моделі або None, якщо все гаразд."""
    if name == "price_info":
        if args.service.lower() not in [v.lower() for v in VALUES_0]:
            # допустимих значень більше 10 — усі не перелічуємо, а підказуємо схожі за написанням
            if len(VALUES_0) <= 10:
                hint = " Доступні: " + ", ".join(VALUES_0) + "."
            else:
                similar = difflib.get_close_matches(args.service.lower(), [v.lower() for v in VALUES_0], n=3, cutoff=0.6)
                hint = (" Схожі назви в довіднику: " + ", ".join(similar) + ".") if similar else ""
            return (f"Помилка: роботи '{args.service}' немає в довіднику.{hint} "
                    "Назва має бути точно як у прайсі: нижній регістр, називний відмінок (наприклад, «заміна масла», а не «заміни масла»). Якщо назва невідома, спочатку скористайся search_service. Виправ значення або повідом користувачу, що даних про це немає.")
    return None
