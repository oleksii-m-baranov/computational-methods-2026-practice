"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів.

Запуск:  python make_task.py      (з каталогу lab4, де лежить data/)

Варіант 10 (догляд за котом). Шість котів різного віку й ваги. Для кожного кота:
  (а) search_articles  - знайти в корпусі статтю за його темою;
  (б) vaccine_info     - знайти в довіднику щеплення (поле «вік першого щеплення»);
  (в) calc_food        - порахувати місячну норму корму: вага * 25 г/кг * 30 днів.
Підсумок: сумарна місячна норма корму всіх шести котів, у грамах.

Скрипт сам звіряється з вашим корпусом і довідником. Якщо слова для пошуку в корпусі
нічого не знаходять, він підбирає інші з назв ваших статей і пише про це.
"""
import json
import os
import re

from checks import VACCINES                       # назви щеплень з data/vaccines.csv
from tools import calc_food, search_articles, vaccine_info

# Шість котів: (кличка, вік, вага в кг, тема - слово для пошуку в корпусі).
# Ваги підібрані так, щоб норма корму виходила цілим числом грамів без округлення.
CATS = [
    ("Мурзик", "кошеня, 3 міс.", 1.5, "дряпає"),       # «Чому кіт дряпає меблі»
    ("Багіра", "кішка, 8 міс.", 3.0, "вух"),          # «Гігієна вух та очей»
    ("Рудий", "кіт, 2 роки", 4.5, "линяння"),         # «Линяння: сезонна норма чи проблема»
    ("Сніжка", "кішка, 4 роки", 3.5, "зубами"),       # «Догляд за зубами кота»
    ("Барсик", "кіт, 7 років", 5.5, "купання"),       # «Купання кота: коли це потрібно»
    ("Маркіз", "кіт, 12 років", 6.0, "активність"),   # «Гра та фізична активність»
]

GRAMS_PER_KG = 25      # норма корму, г на кг ваги на день (задана в питанні явно)
DAYS = 30              # «місячна» норма = 30 днів

# Мінімум викликів інструментів для повного розв'язання: шість котів по три інструменти.
MIN_CALLS = 18


def corpus_titles():
    """Назви статей корпусу (перший рядок кожного файла)."""
    folder = "data/corpus"
    titles = []
    for filename in sorted(os.listdir(folder)):
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            titles.append(f.readline().strip())
    return titles


def found(topic):
    """Чи знаходить search_articles хоч щось за цим словом."""
    return not search_articles(topic).startswith("За запитом")


def pick_topics():
    """Слова для пошуку по одному на кота. Якщо слово нічого не знаходить, беремо інше з назв статей."""
    topics = [cat[3] for cat in CATS]
    reserve = []                                           # запасні слова з назв статей корпусу
    for title in corpus_titles():
        for word in re.findall(r"[а-яіїєґ']{5,}", title.lower()):
            if word not in reserve and found(word):
                reserve.append(word)
    for i, topic in enumerate(topics):
        if found(topic) and topics.count(topic) == 1:
            continue
        spare = [w for w in reserve if w not in topics]
        if not spare:
            raise SystemExit(f"У корпусі не вистачає слів для пошуку (потрібно {len(CATS)} різних).")
        print(f"УВАГА: за словом '{topic}' у корпусі нічого немає, беремо '{spare[0]}'")
        topics[i] = spare[0]
    return topics


def build_question(topics):
    """Текст питання за шаблоном лабораторної: перелік, (а), (б), (в), підсумок."""
    cats = "; ".join(
        f"{name} ({age}, {weight} кг, тема пошуку: {topics[i]}, щеплення: {VACCINES[i % len(VACCINES)]})"
        for i, (name, age, weight, _) in enumerate(CATS))
    return (
        f"Для кожного з шести котів: {cats}. "
        "Для кожного: (а) знайди в корпусі статей статтю за його темою пошуку і наведи назву статті "
        "одним реченням; (б) знайди в довіднику вказане щеплення і назви вік першого щеплення; "
        f"(в) порахуй місячну норму корму: вага кота, помножена на {GRAMS_PER_KG} г на кг на день "
        f"і на {DAYS} днів. "
        "У кінці назви сумарну місячну норму корму всіх шести котів одним числом у грамах."
    )


def cost_of_one(weight):
    """Місячна норма корму одного кота, грами. Рахуємо тим самим інструментом, що й агент."""
    return int(calc_food(weight, GRAMS_PER_KG, DAYS).split()[0])     # «3750 г» -> 3750


def compute():
    """Правильна відповідь: сума по всіх шести котах. Рахуємо самі, без моделі."""
    total = 0
    for _, _, weight, _ in CATS:
        total = total + cost_of_one(weight)
    return total


def save_task(total, question, topics):
    """Записує питання, правильну відповідь і MIN_CALLS у файл long_task.json.

    Ключ reference - довідка для ручної перевірки логів (чи не вигадала модель числа); агент її не бачить.
    """
    reference = [{
        "cat": name,
        "search": f"{topics[i]} -> {search_articles(topics[i])}",
        "vaccine": f"{VACCINES[i % len(VACCINES)]} -> {vaccine_info(VACCINES[i % len(VACCINES)])}",
        "food_g": cost_of_one(weight),
    } for i, (name, _, weight, _) in enumerate(CATS)]
    task = {
        "id": "L1",
        "question": question,
        "expected": format(round(total, 2), "g"),     # число як текст, без зайвих нулів
        "min_calls": MIN_CALLS,
        "reference": reference,
    }
    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


if len(VACCINES) < len(CATS):
    print(f"УВАГА: у довіднику лише {len(VACCINES)} щеплень, тому деякі повторюються "
          "(у звіті згадайте: частина «повторних викликів» - це не вина обрізання).")

topics = pick_topics()
task = save_task(compute(), build_question(topics), topics)
print("Питання:", task["question"])
print("Правильна відповідь:", task["expected"])
print("Файл long_task.json записано")