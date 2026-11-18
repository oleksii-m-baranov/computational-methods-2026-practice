"""Агрегування логів та медіанні показники конфігурацій."""
import statistics
from pathlib import Path
from logparse import parse_log
from metrics import describe

ROOT = Path(__file__).resolve().parent


def make_row(run_id, name, right, seconds):
    text = (ROOT / "logs" / f"{run_id}.log").read_text(encoding="utf-8")
    runs = parse_log(text)
    if not runs:
        raise ValueError(f"Немає даних у {run_id}.log")
    d = describe(runs[0])
    return {"config": name, "right": int(right), "seconds": seconds,
            "steps": d["steps"], "calls": d["tool_calls"],
            "prompt": d["prompt_tokens"], "completion": d["completion_tokens"],
            "extra": d["extra_tokens"], "squeezes": len(d["squeezes"]),
            "repeats": d["repeats"], "cache_hits": d["cache_hits"]}


def print_table(rows):
    if not rows:
        return
    columns = ["config", "right", "steps", "calls", "prompt", "completion", "extra", "seconds", "squeezes", "repeats"]
    labels = ["Режим", "Правильно", "Кроків", "Інструментів", "Вхід", "Вихід", "Підсумов.", "Час, с", "Стиснень", "Повторів"]
    print("| " + " | ".join(labels) + " |")
    print("|" + "|".join("---" for _ in labels) + "|")
    for name in dict.fromkeys(row["config"] for row in rows):
        part = [row for row in rows if row["config"] == name]
        cells = [name, f"{sum(r['right'] for r in part)} з {len(part)}"]
        cells += [f"{statistics.median(r[key] for r in part):g}" for key in columns[2:]]
        print("| " + " | ".join(cells) + " |")
