"""Transparent, task-specific completeness guard for Baranov Lab 4.

Checks *actual successful tool results*; never inserts tool calls, supplies
precomputed expected values, or alters the model's responses. It only requests
missing work when the model tries to stop too early.
"""
import json
import math
import re
from pathlib import Path

ITEMS = (
    ("рис", 150, ("рис",)),
    ("картопля", 200, ("картоп",)),
    ("яблука", 140, ("яблу",)),
    ("гарбуз", 220, ("гарбуз",)),
    ("яйця", 120, ("яйц", "яйц", "яєц")),
    ("макарони", 180, ("макарон",)),
)


def applies_to(task):
    """Do not change the behaviour of other Lab3/Lab4 tasks."""
    path = Path(__file__).resolve().with_name("long_task.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return data.get("min_calls") == 18 and task == data.get("question")


def _args(record):
    args = record.get("args", {})
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            return {}
    return args if isinstance(args, dict) else {}


def _product_matches(value, aliases):
    val = str(value).casefold().strip()
    return any(alias in val for alias in aliases)


def _number(value):
    try:
        return float(str(value).strip().replace(",", "."))
    except (TypeError, ValueError):
        return None


def missing_actions(records):
    """List real, still-missing tasks; verify scale arguments against lookup data."""
    if not isinstance(records, list):
        records = []
    missing = []
    for product, grams, aliases in ITEMS:
        search_ok = False
        kcal = None
        for r in records:
            if not isinstance(r, dict):
                continue
            tool = r.get("tool")
            args = _args(r)
            result = str(r.get("result", ""))
            if tool == "search_recipes" and _product_matches(args.get("query", ""), aliases):
                if "нічого не знайдено" not in result.casefold() and result.strip():
                    search_ok = True
            elif tool == "product_info" and _product_matches(args.get("product", ""), aliases):
                match = re.search(r"калорійність\s*:\s*(\d+(?:[.,]\d+)?)\s*ккал", result, re.I)
                if match:
                    kcal = _number(match.group(1))
        if not search_ok:
            missing.append(f'search_recipes(query="{product}")')
        if kcal is None:
            missing.append(f'product_info(product="{product}")')
            continue
        scaled = False
        for r in records:
            if not isinstance(r, dict) or r.get("tool") != "scale_amount":
                continue
            a = _args(r)
            amount, base, target = (_number(a.get(k)) for k in ("amount", "base_servings", "target_servings"))
            got = _number(r.get("result"))
            if any(x is None for x in (amount, base, target, got)):
                continue
            if (math.isclose(amount, kcal, abs_tol=0.01) and
                math.isclose(base, 100, abs_tol=0.01) and
                math.isclose(target, grams, abs_tol=0.01) and
                math.isclose(got, kcal * grams / 100, abs_tol=0.11)):
                scaled = True
                break
        if not scaled:
            kcal_str = f"{kcal:g}"
            missing.append(f"scale_amount(amount={kcal_str}, base_servings=100, target_servings={grams})")
    return missing


def verify_before_final(records):
    """Return (complete, feedback). Values are always drawn from actual tool results."""
    missing = missing_actions(records)
    if not missing:
        return True, "Усі 18 дій перевірено за результатами інструментів."
    lines = "\n".join(f"- {item}" for item in missing)
    feedback = (
        "Довга задача ще НЕ завершена. Потрібні 3 успішні виклики для КОЖНОГО "
        "з шести продуктів, усі дані перевіряються за реальними результатами інструментів. "
        "Не давай фінальну відповідь зараз. Виконай відсутні виклики "
        "інструментів (можна по одному), не вигадуй значення й не підмінюй "
        "калорійність масою. Наразі бракує:\n" + lines +
        "\nПісля завершення ВСІХ викликів наведи результати для шести продуктів та їхню суму."
    )
    return False, feedback
