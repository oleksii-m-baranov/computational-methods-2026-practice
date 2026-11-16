import csv
with open("data/products.csv", encoding="utf-8") as f:
    PRODUCTS = {row["product"].lower() for row in csv.DictReader(f)}

def check_meaning(name, args):
    if name == "product_info" and args.product.lower() not in PRODUCTS:
        return (f"Помилка: продукту '{args.product}' немає в довіднику. "
                "Потрібна назва наявного продукту в називному відмінку однини; перевір її у data/products.csv. "
                "Виправ назву або повідом користувачу, що даних про цей продукт немає.")
    return None
