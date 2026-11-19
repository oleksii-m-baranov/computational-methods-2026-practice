"""Контрольна відповідь обчислюється інструментами, без моделі."""
import json
import re
from pathlib import Path
from tools import product_info, scale_amount, search_recipes

ITEMS = [("рис",150),("курка",200),("морква",80),("картопля",250),("яблуко",120),("молоко",200)]
QUESTION = 'Для кожної з шести позицій: рис — 150 г, курка — 200 г, морква — 80 г, картопля — 250 г, яблуко — 120 г, молоко — 200 г. Для кожної позиції: (а) знайди в корпусі рецепт із цим продуктом і коротко опиши його; (б) знайди в довіднику калорійність продукту на 100 г; (в) за допомогою інструмента перерахунку обчисли калорійність заданої ваги продукту. Наведи калорійність кожної порції. Наприкінці назви сумарну калорійність усіх шести порцій у ккал.\n\nПрацюй послідовно, по одному продукту, у порядку зі списку.\nДля поточного продукту спочатку виклич search_recipes,\nпотім product_info для цього самого продукту.\nДочекайся результату довідника. Після цього виклич scale_amount:\namount — отримана калорійність на 100 г,\nbase_servings — 100, target_servings — задана вага в грамах.\nПісля отримання результату переходь до наступного продукту.\nЗа одну відповідь викликай лише один інструмент.\nНе підставляй кількість порцій рецепта замість ваги продукту.\nНе завершуй відповідь, поки не опрацюєш усі шість продуктів.\nЯкщо даних немає, прямо зазнач це, не вигадуй числа.\nФінальну відповідь подай українською.'
MIN_CALLS = 18

def calories_of_one(product, grams):
    assert "\n" in search_recipes(product), f"Немає повного рецепта: {product}"
    info = product_info(product)
    match = re.search(r"Калорійність:\s*(\d+(?:[.,]\d+)?)", info)
    if not match:
        raise ValueError(info)
    return float(scale_amount(float(match.group(1).replace(",", ".")), 100, grams))

def build_task():
    total = sum(calories_of_one(p,g) for p,g in ITEMS)
    return dict(id="L1",question=QUESTION,expected=format(round(total,2),"g"),min_calls=MIN_CALLS)

if __name__ == "__main__":
    import os
    os.chdir(Path(__file__).resolve().parent)
    task = build_task()
    p = Path("long_task.json")
    if p.exists():
        if json.loads(p.read_text(encoding="utf-8")) != task:
            raise SystemExit("STOP: existing task differs; it was NOT overwritten.")
        print("TASK VERIFIED (unchanged)")
    else:
        p.write_text(json.dumps(task,ensure_ascii=False,indent=2),encoding="utf-8")
    for product, grams in ITEMS:
        print(product, grams, calories_of_one(product,grams))
    print("EXPECTED:",task["expected"])
