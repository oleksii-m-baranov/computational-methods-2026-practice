"""Розбір лога: показники прогону та таблиця кроків."""
import argparse
from pathlib import Path
import config
from logparse import parse_log
from metrics import describe

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("log")
    parser.add_argument("mode", nargs="?", choices=["steps"])
    args = parser.parse_args()
    path = Path(args.log)
    if not path.is_absolute():
        path = ROOT / path
    runs = parse_log(path.read_text(encoding="utf-8"))
    if not runs:
        parser.error("У журналі не знайдено задач")
    for run in runs:
        d = describe(run)
        print(f"Статус: {d['status']}; кроків: {d['steps']}; викликів інструментів: {d['tool_calls']}")
        print(f"Повторні виклики: {d['repeats']}; влучання в кеш: {d['cache_hits']}")
        print(f"Перший вхід: {d['first_tokens']}; типовий приріст: {d['typical_growth']:g}")
        print(f"Максимум: {d['max_tokens']} ({d['max_tokens']/config.NUM_CTX:.1%} вікна)")
        print(f"Сума prompt_tokens: {d['prompt_tokens']}; за формулою: {d['formula']:g}")
        print(f"Сума completion_tokens: {d['completion_tokens']}; додаткові: {d['extra_tokens']}")
        print(f"Застій на кроці: {d['stall'] or 'не виявлено'}")
        for s in d["squeezes"]:
            used, before, after = s["squeeze"]
            print(f"Стиснення на кроці {s['n']}: {used} токенів, {before} -> {after} повідомлень")
        if args.mode == "steps":
            print("| Крок | prompt_tokens | Приріст | Дія |")
            print("|---:|---:|---:|---|")
            previous = None
            for s in run["steps"]:
                delta = s["tokens"] - previous if previous is not None and s["tokens"] is not None else "—"
                action = "; ".join(s["calls"]) if s["calls"] else ("помилка сервера" if s["server_error"] else "відповідь/перевірка")
                action = action.replace("|", "\\|")
                print(f"| {s['n']} | {s['tokens'] if s['tokens'] is not None else '—'} | {delta} | {action} |")
                if s["tokens"] is not None:
                    previous = s["tokens"]


if __name__ == "__main__":
    main()
