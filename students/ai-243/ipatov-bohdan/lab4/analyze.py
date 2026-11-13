import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
r"""Розбір логів прогонів: що відбувалося з входом моделі.

Запуск:
    python analyze.py logs\probe_none_r1.log           підсумок прогону
    python analyze.py logs\probe_none_r1.log steps     підсумок і таблиця за кроками
"""
import os
import sys

import config
from logparse import parse_log
from metrics import describe


def action_lines(step):
    """Коротко: що зробила модель на цьому кроці. Кожен виклик - окремим рядком."""
    if step["server_error"]:
        return ["ПОМИЛКА СЕРВЕРА"]
    if step["calls"]:
        return [c if len(c) < 60 else c[:57] + "..." for c in step["calls"]]
    if step["answer"]:
        return ["відповідь без виклику"]
    return ["відхилено перевіркою (див. лог)"]


def print_steps(run):
    """Друкує таблицю: крок, prompt_tokens, приріст, що зробила модель."""
    header = ["Крок", "prompt_tokens", "Приріст", "Що зробила модель"]
    rows = []
    previous = None
    for s in run["steps"]:
        growth = ""
        if previous is not None and s["tokens"] is not None:
            growth = s["tokens"] - previous
        actions = action_lines(s)
        rows.append([str(s["n"]), str(s["tokens"]), str(growth), actions[0]])
        rows += [["", "", "", a] for a in actions[1:]]   # решта викликів кроку
        if s["tokens"] is not None:
            previous = s["tokens"]

    # ширина колонки - за найдовшим значенням; числа вирівнюємо праворуч
    widths = [max(len(r[i]) for r in [header] + rows) for i in range(len(header))]
    right = [True, True, True, False]

    def line(cells):
        parts = [c.rjust(w) if r else c.ljust(w) for c, w, r in zip(cells, widths, right)]
        return "| " + " | ".join(parts) + " |"

    print()
    print(line(header))
    print("|" + "|".join("-" * (w + 1) + ":" if r else ":" + "-" * (w + 1)
                         for w, r in zip(widths, right)) + "|")
    for r in rows:
        print(line(r))


def print_summary(run):
    """Друкує показники одного прогону."""
    d = describe(run)
    print(f"  статус завершення            : {d['status']}")
    print(f"  кроків                       : {d['steps']} (повторних викликів: {d['repeats']})")
    print(f"  вхід першого кроку           : {d['first_tokens']} токенів")
    print(f"  типовий приріст за крок      : {d['typical_growth']:.0f} токенів")
    print(f"  найбільший вхід              : {d['max_tokens']} токенів "
          f"({d['max_tokens'] / config.NUM_CTX:.0%} вікна {config.NUM_CTX})")
    print(f"  сума prompt_tokens за прогін : {d['prompt_tokens']}")
    print(f"  за формулою n*C + d*n*(n-1)/2: {d['formula']:.0f}")
    print(f"  вхід перестав рости на кроці : {d['stall'] or 'не помічено'}")
    print(f"  влучань у кеш                : {d['cache_hits']}")
    for s in d["squeezes"]:
        before, msgs_before, msgs_after = s["squeeze"]
        print(f"  стиснення на кроці {s['n']}: вхід був {before}, "
              f"повідомлень {msgs_before} -> {msgs_after}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)

    # відносний шлях рахуємо від теки скрипта, щоб не залежати від робочої теки
    path_to_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[1])
    with open(path_to_log, encoding="utf-8") as f:
        runs = parse_log(f.read())

    for run in runs:
        print(f"\nПрогін: {run['task'][:60]}")
        print_summary(run)
        if len(sys.argv) > 2 and sys.argv[2] == "steps":
            print_steps(run)