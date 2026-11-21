"""Перевірки змісту аргументів. Варіант 9 — Вибір ноутбука."""
import csv
import difflib
import os

with open("data/laptops.csv", encoding="utf-8") as f:
    CATALOG = [row for row in csv.DictReader(f)]

MODELS = [row["model"] for row in CATALOG]
PRICES = {float(row["price"]) for row in CATALOG}

CORPUS_MODELS = []
for filename in sorted(os.listdir("data/corpus")):
    with open(os.path.join("data/corpus", filename), encoding="utf-8") as f:
        CORPUS_MODELS.append(f.readline().strip())


def check_meaning(name, args):
    if name == "laptop_info":
        matched = [m for m in MODELS if m.lower() == args.model.strip().lower()]
        if not matched:
            if args.model.strip().lower() in [m.lower() for m in CORPUS_MODELS]:
                return (
                    f"Помилка: модель '{args.model}' присутня в описах каталогу, "
                    "але відсутня у довіднику цін і наявності. "
                    "Не вигадуй ціну — повідом користувачу, що даних про ціну "
                    f"та наявність '{args.model}' у довіднику немає."
                )
            hints = difflib.get_close_matches(args.model.strip(), MODELS, n=2, cutoff=0.6)
            hint_str = f"Можливо, мається на увазі: {', '.join(hints)}. " if hints else ""
            return (
                f"Помилка: моделі '{args.model}' немає в довіднику. "
                f"{hint_str}"
                "Точну назву моделі можна дізнатися пошуком через search_laptops. "
                "Виправ назву моделі або повідом користувачу, що даних про неї немає."
            )

    if name == "calc_installment":
        if args.price not in PRICES:
            return (
                f"Помилка: ціни {args.price:g} грн немає в довіднику ноутбуків. "
                "Допустимі лише реальні ціни моделей із довідника. "
                "Спершу дізнайся точну ціну обраної моделі через laptop_info і передай її."
            )

    return None
