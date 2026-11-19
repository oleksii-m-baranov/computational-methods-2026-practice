"""Аналіз журналів лабораторної роботи №4.

Команди:
    python analyze.py
    python analyze.py logs/testfixed_none_r1.log
    python analyze.py logs/testfixed_none_r1.log steps

Підтримує старий і новий формати журналів agent.py.
"""

import csv
import json
import re
import statistics
import sys

from collections import defaultdict
from pathlib import Path

import config


MODES = ["none", "trim", "trim+state"]

STEP_RE = re.compile(
    r"---\s*крок\s+(\d+).*?"
    r"prompt_tokens=(\d+).*?"
    r"completion_tokens=(\d+)",
    re.IGNORECASE
)

CALL_RE = re.compile(
    r"^\s*виклик(?:\s+\d+/\d+)?\s*:\s*(.*)$",
    re.IGNORECASE
)

CACHE_RE = re.compile(
    r"^\s*КЕШ:\s*(HIT|MISS)",
    re.IGNORECASE
)

SQUEEZE_RE = re.compile(
    r"СТИСНЕННЯ:.*?вхід був\s+(\d+).*?"
    r"повідомлень\s+(\d+)\s*->\s*(\d+)",
    re.IGNORECASE
)

SUMMARY_RE = re.compile(
    r"ПІДСУМОК ВИКЛИКІВ:\s*"
    r"реальних=(\d+),\s*"
    r"повторних=(\d+),\s*"
    r"відхилених=(\d+)",
    re.IGNORECASE
)

SERVER_ERROR_RE = re.compile(
    r"ПОМИЛКА СЕРВЕРА|SERVER_ERROR|Request timed out",
    re.IGNORECASE
)


def normalize_call(call):
    """Нормалізує JSON-аргументи для пошуку повторів."""
    call = call.strip()

    match = re.match(
        r"^([A-Za-z_]\w*)\((.*)\)$",
        call,
        re.DOTALL
    )

    if not match:
        return call

    name = match.group(1)
    arguments = match.group(2)

    try:
        parsed = json.loads(arguments)

        normalized = json.dumps(
            parsed,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":")
        )

        return f"{name}({normalized})"

    except (ValueError, TypeError):
        return call


def empty_step(number, tokens, completion, cache):
    return {
        "n": number,
        "tokens": tokens,
        "completion": completion,
        "calls": [],
        "answer": False,
        "server_error": False,
        "cache": cache,
        "squeeze": None,
        "real_calls": 0,
        "duplicate_calls": 0,
        "limited_calls": 0,
        "summary_present": False,
    }


def read_single_log(path):
    """Читає журнал та визначає кроки й події."""
    text = path.read_text(encoding="utf-8-sig")

    steps = []
    current = None
    pending_cache = None

    status = "unknown"
    server_errors = 0
    server_timeouts = 0

    for line in text.splitlines():

        cache_match = CACHE_RE.search(line)

        if cache_match:
            pending_cache = cache_match.group(1).upper()

        step_match = STEP_RE.search(line)

        if step_match:
            current = empty_step(
                int(step_match.group(1)),
                int(step_match.group(2)),
                int(step_match.group(3)),
                pending_cache
            )

            steps.append(current)
            pending_cache = None
            continue

        upper = line.upper()

        if "ПОМИЛКА СЕРВЕРА" in upper:
            server_errors += 1

            if "TIMEOUT" in upper or "TIMED OUT" in upper:
                server_timeouts += 1

            if current is not None:
                current["server_error"] = True

            status = "server_error"

        if current is None:
            if line.lstrip().startswith("СТОП:"):
                status = "stopped"
            continue

        call_match = CALL_RE.search(line)

        if call_match:
            current["calls"].append(
                call_match.group(1).strip()
            )

        summary_match = SUMMARY_RE.search(line)

        if summary_match:
            current["real_calls"] = int(
                summary_match.group(1)
            )

            current["duplicate_calls"] = int(
                summary_match.group(2)
            )

            current["limited_calls"] = int(
                summary_match.group(3)
            )

            current["summary_present"] = True

        squeeze_match = SQUEEZE_RE.search(line)

        if squeeze_match:
            current["squeeze"] = (
                int(squeeze_match.group(1)),
                int(squeeze_match.group(2)),
                int(squeeze_match.group(3))
            )

        if (
            "ВІДПОВІДЬ:" in upper
            or "ВІДПОВІДЬ АГЕНТА:" in upper
        ):
            current["answer"] = True
            status = "final"

        if line.lstrip().startswith("СТОП:"):
            status = "stopped"

    return {
        "path": str(path),
        "steps": steps,
        "status": status,
        "server_errors": server_errors,
        "server_timeouts": server_timeouts,
    }


def count_repeats(steps):
    """Рахує однакові запропоновані виклики."""
    seen = set()
    repeats = 0

    for step in steps:
        for call in step["calls"]:
            normalized = normalize_call(call)

            if normalized in seen:
                repeats += 1
            else:
                seen.add(normalized)

    return repeats


def count_call_metrics(steps):
    """Повертає реальні, повторні та відхилені виклики."""
    real = 0
    duplicate = 0
    limited = 0

    seen = set()

    for step in steps:

        if step["summary_present"]:
            real += step["real_calls"]
            duplicate += step["duplicate_calls"]
            limited += step["limited_calls"]

            for call in step["calls"]:
                seen.add(normalize_call(call))

        else:
            # Старий формат: кожний записаний виклик
            # фактично передавався до dispatcher.
            real += len(step["calls"])

            for call in step["calls"]:
                normalized = normalize_call(call)

                if normalized in seen:
                    duplicate += 1
                else:
                    seen.add(normalized)

    return {
        "real": real,
        "duplicate": duplicate,
        "limited": limited,
        "proposed": sum(
            len(step["calls"]) for step in steps
        )
    }


def typical_growth(steps):
    tokens = [
        step["tokens"]
        for step in steps
    ]

    growth = [
        after - before
        for before, after in zip(
            tokens,
            tokens[1:]
        )
        if after > before
    ]

    return (
        statistics.median(growth)
        if growth
        else 0
    )


def find_stall(steps, typical):
    for previous, current in zip(
        steps,
        steps[1:]
    ):
        near_window = (
            current["tokens"] >=
            0.8 * config.NUM_CTX
        )

        stopped_growing = (
            current["tokens"] - previous["tokens"]
            <= 0.2 * typical
        )

        if near_window and stopped_growing:
            return current["n"]

    return None


def describe_single(run):
    steps = run["steps"]

    n = len(steps)
    first = steps[0]["tokens"] if steps else 0
    typical = typical_growth(steps)

    calls = count_call_metrics(steps)

    return {
        "status": run["status"],
        "steps": n,
        "repeats": count_repeats(steps),
        "real_calls": calls["real"],
        "duplicate_calls": calls["duplicate"],
        "limited_calls": calls["limited"],
        "proposed_calls": calls["proposed"],
        "first_tokens": first,
        "typical_growth": typical,
        "max_tokens": max(
            (
                step["tokens"]
                for step in steps
            ),
            default=0
        ),
        "prompt_tokens": sum(
            step["tokens"]
            for step in steps
        ),
        "completion_tokens": sum(
            step["completion"]
            for step in steps
        ),
        "formula": (
            n * first
            + typical * n * (n - 1) / 2
        ),
        "stall": find_stall(
            steps,
            typical
        ),
        "cache_hits": sum(
            step["cache"] == "HIT"
            for step in steps
        ),
        "cache_misses": sum(
            step["cache"] == "MISS"
            for step in steps
        ),
        "squeezes": [
            step
            for step in steps
            if step["squeeze"] is not None
        ],
        "server_errors": run["server_errors"],
        "server_timeouts": run["server_timeouts"],
    }


def print_single_summary(run):
    data = describe_single(run)

    percent = (
        data["max_tokens"]
        / config.NUM_CTX * 100
        if config.NUM_CTX
        else 0
    )

    print()
    print("АНАЛІЗ ОДНОГО ПРОГОНУ")
    print("=" * 65)

    print(f"Лог: {run['path']}")
    print(f"Статус завершення: {data['status']}")
    print(f"Кроків з відповіддю моделі: {data['steps']}")

    print(
        f"Запропоновано викликів: "
        f"{data['proposed_calls']}"
    )

    print(
        f"Реально виконано викликів: "
        f"{data['real_calls']}"
    )

    print(
        f"Повторно використано результатів: "
        f"{data['duplicate_calls']}"
    )

    print(
        f"Відхилено через ліміт: "
        f"{data['limited_calls']}"
    )

    print(
        f"Повторних пропозицій моделі: "
        f"{data['repeats']}"
    )

    print(
        f"Вхід першого кроку: "
        f"{data['first_tokens']} токенів"
    )

    print(
        f"Типовий приріст за крок: "
        f"{data['typical_growth']:g} токенів"
    )

    print(
        f"Найбільший вхід: "
        f"{data['max_tokens']} токенів "
        f"({percent:.1f}% вікна {config.NUM_CTX})"
    )

    print(
        f"Сума prompt_tokens: "
        f"{data['prompt_tokens']}"
    )

    print(
        "За формулою n*C + d*n*(n-1)/2: "
        f"{data['formula']:g}"
    )

    print(
        "Вхід перестав рости на кроці: "
        f"{data['stall'] or 'не помічено'}"
    )

    print(
        f"Влучань у кеш: "
        f"{data['cache_hits']}"
    )

    print(
        f"Помилок запиту до сервера: "
        f"{data['server_errors']}"
    )

    print(
        f"Із них тайм-аутів: "
        f"{data['server_timeouts']}"
    )

    for step in data["squeezes"]:
        used, before, after = step["squeeze"]

        print(
            f"Стиснення на кроці {step['n']}: "
            f"вхід був {used}, "
            f"повідомлень {before} -> {after}"
        )


def print_steps(run):
    header = [
        "Крок",
        "prompt_tokens",
        "Приріст",
        "Що зробила модель",
    ]

    rows = []
    previous = None

    for step in run["steps"]:
        growth = ""

        if previous is not None:
            growth = str(
                step["tokens"] - previous
            )

        if step["calls"]:
            actions = step["calls"]

        elif step["answer"]:
            actions = [
                "відповідь без виклику"
            ]

        else:
            actions = [
                "немає викликів інструментів"
            ]

        for index, action in enumerate(actions):
            short_action = (
                action[:77] + "..."
                if len(action) > 80
                else action
            )

            rows.append([
                str(step["n"]) if index == 0 else "",
                str(step["tokens"]) if index == 0 else "",
                growth if index == 0 else "",
                short_action,
            ])

        previous = step["tokens"]

    if not rows:
        print("Немає даних для таблиці.")
        return

    widths = [
        max(
            len(str(row[i]))
            for row in [header] + rows
        )
        for i in range(len(header))
    ]

    def format_row(row):
        return "| " + " | ".join(
            str(value).ljust(width)
            for value, width in zip(
                row,
                widths
            )
        ) + " |"

    print()
    print("ТАБЛИЦЯ 2 — ЗРОСТАННЯ ВХОДУ")
    print()

    print(format_row(header))

    print(
        "| "
        + " | ".join(
            "-" * width
            for width in widths
        )
        + " |"
    )

    for row in rows:
        print(format_row(row))


def load_results():
    """Зчитує результати всіх експериментів."""
    results = []

    for path in sorted(
        Path("results").glob("*.json")
    ):
        if path.name in {
            "analysis.json",
            "summary.json",
            "comparison.json"
        }:
            continue

        try:
            with open(
                path,
                encoding="utf-8"
            ) as file:
                data = json.load(file)

        except (OSError, ValueError):
            continue

        if not isinstance(data, dict):
            continue

        if (
            "run_id" not in data
            or data.get("mode") not in MODES
        ):
            continue

        log_path = Path(
            data.get("log_path") or ""
        )

        if not log_path.is_file():
            alternative = (
                Path("logs")
                / f"{data['run_id']}.log"
            )

            if alternative.is_file():
                log_path = alternative
            else:
                print(
                    f"Лог не знайдено: "
                    f"{data['run_id']}"
                )
                continue

        run = read_single_log(log_path)

        if not run["steps"]:
            continue

        metrics = describe_single(run)

        results.append({
            "run_id": data["run_id"],
            "tag": data.get("tag", ""),
            "mode": data["mode"],
            "repeat": data.get("repeat", 1),
            "num_ctx": data.get(
                "num_ctx",
                config.NUM_CTX
            ),
            "elapsed_seconds": data.get(
                "elapsed_seconds",
                0
            ),
            "correct": data.get(
                "correct",
                False
            ),
            "steps": metrics["steps"],
            "tool_calls": metrics["real_calls"],
            "proposed_calls": metrics["proposed_calls"],
            "repeated_calls": metrics["repeats"],
            "reused_calls": metrics["duplicate_calls"],
            "limited_calls": metrics["limited_calls"],
            "first_prompt_tokens": metrics["first_tokens"],
            "total_prompt_tokens": metrics["prompt_tokens"],
            "total_completion_tokens": metrics["completion_tokens"],
            "max_prompt_tokens": metrics["max_tokens"],
            "context_usage_percent": round(
                metrics["max_tokens"]
                / data.get(
                    "num_ctx",
                    config.NUM_CTX
                ) * 100,
                2
            ),
            "context_growth": metrics["typical_growth"],
            "median_delta": metrics["typical_growth"],
            "predicted_total_tokens": metrics["formula"],
            "context_overflow": (
                metrics["max_tokens"]
                > data.get(
                    "num_ctx",
                    config.NUM_CTX
                )
            ),
            "compressions": len(
                metrics["squeezes"]
            ),
            "cache_hits": metrics["cache_hits"],
            "cache_misses": metrics["cache_misses"],
            "server_errors": metrics["server_errors"],
            "server_timeouts": metrics["server_timeouts"],
            "has_answer": (
                metrics["status"] == "final"
            ),
            "stopped": (
                metrics["status"] == "stopped"
            ),
        })

    return results


def make_summary(results):
    groups = defaultdict(list)

    for item in results:
        key = (
            item["tag"],
            item["mode"],
            item["num_ctx"]
        )

        groups[key].append(item)

    summary = []

    for (tag, mode, num_ctx), items in sorted(
        groups.items()
    ):
        def med(field):
            return statistics.median(
                item[field]
                for item in items
            )

        summary.append({
            "tag": tag,
            "mode": mode,
            "num_ctx": num_ctx,
            "runs": len(items),
            "median_time_seconds": round(
                med("elapsed_seconds"),
                2
            ),
            "median_steps": med("steps"),
            "median_tool_calls": med("tool_calls"),
            "median_proposed_calls": med("proposed_calls"),
            "median_reused_calls": med("reused_calls"),
            "median_limited_calls": med("limited_calls"),
            "median_prompt_tokens": med(
                "total_prompt_tokens"
            ),
            "median_completion_tokens": med(
                "total_completion_tokens"
            ),
            "median_max_prompt_tokens": med(
                "max_prompt_tokens"
            ),
            "median_compressions": med(
                "compressions"
            ),
            "median_repeated_calls": med(
                "repeated_calls"
            ),
            "median_server_timeouts": med(
                "server_timeouts"
            ),
            "correct_runs": sum(
                bool(item["correct"])
                for item in items
            )
        })

    return summary


def save_csv(path, rows):
    if not rows:
        return

    with open(
        path,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(
                rows[0].keys()
            )
        )

        writer.writeheader()
        writer.writerows(rows)


def analyze():
    Path("results").mkdir(
        exist_ok=True
    )

    results = load_results()

    if not results:
        print(
            "Немає результатів для аналізу."
        )
        return

    summary = make_summary(results)

    analysis_json = Path(
        "results/analysis.json"
    )

    analysis_csv = Path(
        "results/analysis.csv"
    )

    summary_json = Path(
        "results/summary.json"
    )

    summary_csv = Path(
        "results/summary.csv"
    )

    analysis_json.write_text(
        json.dumps(
            results,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    summary_json.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    save_csv(
        analysis_csv,
        results
    )

    save_csv(
        summary_csv,
        summary
    )

    print()
    print("АНАЛІЗ ЛР4")
    print("=" * 60)

    print(
        f"Проаналізовано запусків: "
        f"{len(results)}"
    )

    print(
        f"Груп результатів: "
        f"{len(summary)}"
    )

    for item in summary:
        print()
        print(f"Тег: {item['tag']}")
        print(f"Режим: {item['mode']}")
        print(f"Контекст: {item['num_ctx']}")
        print(f"Запусків: {item['runs']}")

        print(
            f"Медіана часу: "
            f"{item['median_time_seconds']} с"
        )

        print(
            f"Медіана кроків: "
            f"{item['median_steps']}"
        )

        print(
            f"Медіана реальних викликів: "
            f"{item['median_tool_calls']}"
        )

        print(
            f"Медіана повторно використаних: "
            f"{item['median_reused_calls']}"
        )

        print(
            f"Медіана вхідних токенів: "
            f"{item['median_prompt_tokens']}"
        )

        print(
            f"Медіана стиснень: "
            f"{item['median_compressions']}"
        )

        print(
            f"Правильних запусків: "
            f"{item['correct_runs']}/{item['runs']}"
        )

    print()
    print(f"Детальний JSON: {analysis_json}")
    print(f"Детальний CSV: {analysis_csv}")
    print(f"Підсумковий JSON: {summary_json}")
    print(f"Підсумковий CSV: {summary_csv}")


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        path = Path(sys.argv[1])

        if not path.is_absolute():
            path = (
                Path(__file__).resolve().parent
                / path
            )

        if not path.is_file():
            print(
                f"Файл не знайдено: {path}"
            )
            sys.exit(1)

        run = read_single_log(path)

        if not run["steps"]:
            print(
                "У файлі не знайдено "
                "кроків агента."
            )
            sys.exit(1)

        print_single_summary(run)

        if (
            len(sys.argv) >= 3
            and sys.argv[2] == "steps"
        ):
            print_steps(run)

    else:
        analyze()
