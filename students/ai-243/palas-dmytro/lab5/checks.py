"""Перевірки змісту аргументів."""
import csv

with open("data/materials.csv", encoding="utf-8") as f:
    MATERIALS = [row["material"].lower() for row in csv.DictReader(f)]


def check_meaning(name, args):
    if name == "search_works":
        if not args.query.strip():
            return (
                "Помилка: пошуковий запит не може бути порожнім. "
                "Передай одне-два слова українською (тип роботи або категорію), "
                "наприклад назву оздоблювальних робіт."
            )

    if name == "material_info":
        if args.material.lower() not in MATERIALS:
            return (
                f"Помилка: матеріалу '{args.material}' немає в довіднику. "
                "У довіднику вказано базові назви матеріалів у нижньому регістрі без одиниці виміру "
                "(наприклад, без слів 'рулон', 'мішок', 'банка'). "
                "Уточни назву матеріалу за цією схемою або повідом користувачу, що даних про цей матеріал немає."
            )
    return None
