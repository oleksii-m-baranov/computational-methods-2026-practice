"""Таблиці за results/rag.csv: підсумок і розподіл поламок за описами інструмента."""
import csv
import statistics

with open("results/rag.csv", encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))
configs = sorted({r["config"] for r in rows})
CATEGORIES = [("ok", "Правильно (питання з відповіддю)"),
              ("no_search", "Не шукав і відповів неправильно"),
              ("miss", "Шукав, але потрібного фрагмента в результаті немає"),
              ("ignored", "Фрагмент у результаті був, відповідь неправильна"),
              ("refused", "Без відповіді: повідомив, що ціна невідома"),
              ("invented", "Без відповіді: вигадав ціну"),
              ("empty", "Без відповіді: порожній результат"),
              ("misrouted", "Без відповіді: неправильно зрозумів запит")]


def med(part, field):
    return statistics.median(float(r[field]) for r in part)


print("Підсумок за описами (по всіх повторах)")
print(f"{'опис':5} {'правильно':>10} {'шукав':>8} {'кроків':>7} {'токенів входу':>14} {'час, с':>7}")
for name in configs:
    part = [r for r in rows if r["config"] == name]
    answerable = [r for r in part if r["kind"] != "none"]
    right = sum(int(r["correct"]) for r in answerable)
    searched = sum(1 for r in answerable if int(r["searches"]) > 0)
    print(f"{name:5} {right:>4}/{len(answerable):<5} {searched:>3}/{len(answerable):<4} {med(part, 'steps'):7.1f} "
          f"{med(part, 'prompt_tokens'):14.0f} {med(part, 'seconds'):7.1f}")

print("\nПоламки (кількість прогонів)")
print(f"{'':58}" + "".join(f"{c:>6}" for c in configs))
for key, title in CATEGORIES:
    counts = [sum(1 for r in rows if r["config"] == c and r["category"] == key) for c in configs]
    print(f"{title:58}" + "".join(f"{n:6}" for n in counts))
