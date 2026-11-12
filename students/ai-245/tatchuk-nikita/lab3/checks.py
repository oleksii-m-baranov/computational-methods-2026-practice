"""Перевірки змісту аргументів."""
import csv

with open("data/materials.csv", encoding="utf-8") as f:
    MATERIALS = list(csv.DictReader(f))

MATERIAL_NAMES = [row["material"] for row in MATERIALS]

# пари (покриття, ціна), які реально є в довіднику
PAIRS = [(float(row["coverage_m2"]), float(row["price"])) for row in MATERIALS]


def check_meaning(name, args):
    if name == "material_info":
        # ключ довідника: назва матеріалу має бути в materials.csv
        if args.material.lower() not in MATERIAL_NAMES:
            return (f"Помилка: матеріалу '{args.material}' немає в довіднику. "
                    "Назва має дослівно збігатися з довідником: повна назва в нижньому регістрі "
                    "й у називному відмінку, наприклад: ґрунтовка, ламінат. "
                    "Виправ назву матеріалу або повідом користувачу, що даних про цей матеріал немає.")

    if name == "calc_materials":
        # правило для двох аргументів: покриття й ціна мають належати одному рядку довідника
        if (args.coverage_m2, args.price) not in PAIRS:
            return (f"Помилка: у довіднику немає матеріалу з покриттям {args.coverage_m2} м² "
                    f"і ціною {args.price} грн. "
                    "Покриття й ціна мають бути взяті з результату material_info для одного матеріалу. "
                    "Спочатку виклич material_info, потім передай отримані значення в calc_materials.")
    return None
