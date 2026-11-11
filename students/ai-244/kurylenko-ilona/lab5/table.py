"""Підсумкова таблиця вартості: медіани по конфігураціях."""

import statistics

from logparse import parse_log
from metrics import describe


def make_row(run_id, name, right, seconds):
    """Формує рядок результатів одного прогону."""
    with open(f"logs/{run_id}.log", encoding="utf-8") as f:
        d = describe(parse_log(f.read())[0])

    return {
        "config": name,
        "right": int(right),
        "seconds": seconds,
        "steps": d["steps"],
        "prompt": d["prompt_tokens"],
        "completion": d["completion_tokens"],
        "extra": d["extra_tokens"],
        "squeezes": len(d["squeezes"]),
        "repeats": d["repeats"],
    }


def print_table(rows):
    """Друкує медіани показників для кожної конфігурації."""
    head = [
        "Конфігурація",
        "Правильно",
        "Кроків",
        "Токенів на вхід",
        "Токенів на вихід",
        "На підсумовування",
        "Час, с",
        "Стиснень",
        "Повторних викликів",
    ]

    lines = []

    for name in dict.fromkeys(r["config"] for r in rows):
        part = [r for r in rows if r["config"] == name]

        def med(field):
            return f"{statistics.median(r[field] for r in part):g}"

        lines.append([
            name,
            f"{sum(r['right'] for r in part)} з {len(part)}",
            med("steps"),
            med("prompt"),
            med("completion"),
            med("extra"),
            med("seconds"),
            med("squeezes"),
            med("repeats"),
        ])

    widths = [
        max(len(line[i]) for line in [head] + lines)
        for i in range(len(head))
    ]

    def show(cells):
        print(
            "| " + " | ".join(
                c.ljust(w) if i == 0 else c.rjust(w)
                for i, (c, w) in enumerate(zip(cells, widths))
            ) + " |"
        )

    print()
    show(head)

    print(
        "|" + "|".join(
            "-" * (w + 2) if i == 0 else "-" * (w + 1) + ":"
            for i, w in enumerate(widths)
        ) + "|"
    )

    for line in lines:
        show(line)