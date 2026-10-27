import csv
import os


def search_recipes(query: str) -> str:
    stopwords = {"з", "із", "та", "і", "й", "у", "в", "на"}

    words = [
        word.lower().strip(".,!?;:()[]{}\"'")
        for word in query.split()
        if word.lower().strip(".,!?;:()[]{}\"'") not in stopwords
    ]

    normalized_words = []

    for word in words:
        if word.startswith("кур"):
            normalized_words.append("кур")
        else:
            normalized_words.append(word)

    found = []
    folder = os.path.join("data", "corpus")

    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(folder, filename)

        with open(path, encoding="utf-8") as f:
            text = f.read()

        searchable = text.lower()

        if normalized_words and any(
            word in searchable for word in normalized_words
        ):
            found.append(text.splitlines()[0])

    if not found:
        return f"За запитом '{query}' нічого не знайдено."

    return " | ".join(found)


def product_info(product: str) -> str:
    with open(
        "data/products.csv",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = (row.get("product") or "").strip()

            if name.lower() == product.strip().lower():
                return (
                    f"Калорійність: {row['kcal_per_100g']} ккал "
                    f"на 100 г, ціна: {row['price_per_kg']} грн/кг"
                )

    return f"Продукту '{product}' немає в довіднику."


def scale_amount(
    amount: float,
    base_servings: float,
    target_servings: float
) -> str:
    if base_servings <= 0:
        return "Помилка: кількість порцій має бути більшою за нуль."

    return str(round(amount * target_servings / base_servings, 1))


TOOLS = {
    "search_recipes": search_recipes,
    "product_info": product_info,
    "scale_amount": scale_amount,
}