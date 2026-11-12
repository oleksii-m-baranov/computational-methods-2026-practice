"""Чернетка таблиць для звіту з lab2.log. Оцінки 1/0 і висновки — вручну!
Запуск: python analyze_log.py"""
import re

text = open("lab2.log", encoding="utf-8").read()
blocks = re.split(r"\n=== ", text)[1:]
print("| Задача | Кроків | Викликів | Правильно (1/0) | Які поламки (авто-підказка) |")
print("|---|---|---|---|---|")
tot = {}
for b in blocks:
    tid = b.split(" |")[0]
    steps = len(re.findall(r"--- крок", b))
    calls = re.findall(r"виклик\s+: (\w+\(.*\))", b)
    results = re.findall(r"результат: (.*)", b)
    ans = re.search(r"ВІДПОВІДЬ: (.*)", b, re.S)
    br = []
    if not calls: br.append("Не викликав інструмент")
    if any(r.startswith("Помилка") for r in results): br.append("Неправильні аргументи")
    if len(calls) != len(set(calls)): br.append("Зациклився")
    if "СТОП" in b: br.append("Вичерпав ліміт кроків")
    for x in br: tot[x] = tot.get(x, 0) + 1
    print(f"| {tid} | {steps} | {len(calls)} | ? | {', '.join(br) or '—'} |")
print("\nАвто виявляє лише 4 з 7 поламок. 'Не той інструмент', 'Не використав результат'")
print("та 'Вигадав результат' перевірте самі, порівнявши ВІДПОВІДЬ з 'результат' у логу.")
print("Підсумок (авто):", tot)
