"""Перевірки змісту аргументів (варіант 9 – вибір ноутбука)."""
import csv
import difflib
import os

# довідник: модель -> рядок з ціною, наявністю, гарантією
with open("data/laptops.csv", encoding="utf-8") as f:
    CATALOG = {row["model"]: row for row in csv.DictReader(f)}

# допустимі ціни – лише ті, що є в довіднику
PRICES = {float(row["price"]) for row in CATALOG.values()}

# назви моделей з корпусу описів (перший рядок кожного файла)
CORPUS_MODELS = []
for filename in sorted(os.listdir("data/corpus")):
    with open(os.path.join("data/corpus", filename), encoding="utf-8") as f:
        CORPUS_MODELS.append(f.readline().strip())


def find_model(name):
    """Шукає модель у довіднику так само, як laptop_info: без урахування регістру."""
    for model in CATALOG:
        if model.lower() == name.strip().lower():
            return model
    return None


def check_meaning(name, args):
    # ключ довідника: модель має бути в laptops.csv
    if name == "laptop_info":
        if find_model(args.model) is None:
            # модель описана в корпусі, але в довіднику її немає (ArtLine Studio 15)
            if args.model.strip().lower() in [m.lower() for m in CORPUS_MODELS]:
                return (f"Помилка: модель '{args.model}' є в описах каталогу, "
                        "але її немає в довіднику цін і наявності. "
                        "Не вигадуй ціну, повідом користувачу, що даних про ціну "
                        "й наявність цієї моделі немає.")
            hint = difflib.get_close_matches(args.model, list(CATALOG), n=2, cutoff=0.6)
            text = f"Помилка: моделі '{args.model}' немає в довіднику. "
            if hint:
                text += f"Можливо, мається на увазі: {', '.join(hint)}. "
            text += ("Точну назву моделі можна дізнатися через search_laptops. "
                     "Виправ назву або повідом користувачу, що такої моделі немає.")
            return text

    # ціна для розстрочки має бути взята з довідника, а не вигадана
    if name == "calc_installment":
        if args.price not in PRICES:
            return (f"Помилка: ціни {args.price:g} грн немає в довіднику. "
                    "Спершу дізнайся ціну обраної моделі через laptop_info "
                    "і передай саме її.")
    return None
