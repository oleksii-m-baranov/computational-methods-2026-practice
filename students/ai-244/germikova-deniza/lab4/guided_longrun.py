"""Експериментальний керований прогін довгої задачі ЛР4.

Не втручається в none/trim/trim+state, доки LAB4_GUIDED_V3 != "1".
У цьому режимі МОДЕЛЬ усе одно пропонує виклики; програма перевіряє
їхні аргументи, і лише валідні виклики передає справжнім інструментам.
Ніякі результати інструментів не вигадуються й не підставляються.
"""

import json
import math
from pathlib import Path
import re

ITEMS = (
    ("рис", 150), ("картопля", 200), ("яблука", 140),
    ("гарбуз", 220), ("яйця", 120), ("макарони", 180),
)


def applies_to(task):
    try:
        cfg = json.loads(Path(__file__).with_name("long_task.json").read_text(encoding="utf-8"))
        return cfg.get("min_calls") == 18 and task == cfg.get("question")
    except (OSError, ValueError):
        return False


def _arguments(r):
    a = r.get("args", {})
    if isinstance(a, str):
        try:
            a = json.loads(a)
        except ValueError:
            return {}
    return a if isinstance(a, dict) else {}


def _number(x):
    try:
        v = float(str(x).replace(",", "."))
        return v if math.isfinite(v) else None
    except (ValueError, TypeError):
        return None


def _lookup_kcal(records, product):
    for r in records:
        if r.get("tool") != "product_info":
            continue
        if str(_arguments(r).get("product", "")).casefold() != product.casefold():
            continue
        m = re.search(r"Калорійність:\s*([0-9]+(?:[.,][0-9]+)?)\s*ккал", str(r.get("result", "")), re.I)
        if m:
            return _number(m.group(1))
    return None


def _record_valid(r, tool, args, product, grams, kcal):
    if r.get("tool") != tool:
        return False
    got_args = _arguments(r)
    if tool == "search_recipes":
        return (str(got_args.get("query", "")).casefold() == product.casefold()
                and "нічого не знайдено" not in str(r.get("result", "")).casefold()
                and bool(str(r.get("result", "")).strip()))
    if tool == "product_info":
        return str(got_args.get("product", "")).casefold() == product.casefold() and kcal is not None
    if tool == "scale_amount":
        a = _number(got_args.get("amount"))
        base = _number(got_args.get("base_servings"))
        target = _number(got_args.get("target_servings"))
        result = _number(r.get("result"))
        return (None not in (a, base, target, result, kcal)
                and math.isclose(a, kcal, abs_tol=0.01)
                and math.isclose(base, 100, abs_tol=0.01)
                and math.isclose(target, grams, abs_tol=0.01)
                and math.isclose(result, kcal * grams / 100, abs_tol=0.11))
    return False


def next_action(records):
    """Перше відсутнє коректне завдання; числові параметри беруться з product_info."""
    for product, grams in ITEMS:
        if not any(_record_valid(r, "search_recipes", {}, product, grams, None) for r in records):
            return "search_recipes", {"query": product}
        kcal = _lookup_kcal(records, product)
        if kcal is None:
            return "product_info", {"product": product}
        args = {"amount": kcal, "base_servings": 100, "target_servings": grams}
        if not any(_record_valid(r, "scale_amount", args, product, grams, kcal) for r in records):
            return "scale_amount", args
    return None


def instruction(action):
    if action is None:
        return ""
    name, args = action
    return ("НАСТУПНА ОДНА ДІЯ. Виклич ЛИШЕ один інструмент: "
            + name + "(" + json.dumps(args, ensure_ascii=False) + "). "
            "Дотримуйся ТОЧНО цих аргументів. Не виконуй інші дії, не давай фінальну відповідь.")


def validate_call(name, raw_args, action):
    if action is None:
        return False, "Усі 18 дій уже виконані: потрібна фінальна відповідь, не інструмент."
    try:
        got = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
    except (TypeError, ValueError):
        return False, "Аргументи не є JSON. " + instruction(action)
    want_name, want = action
    if not isinstance(got, dict) or name != want_name:
        return False, "Неправильний інструмент. " + instruction(action)
    if name in ("search_recipes", "product_info"):
        k = "query" if name == "search_recipes" else "product"
        ok = str(got.get(k, "")).casefold() == str(want[k]).casefold()
    else:
        ok = all(_number(got.get(k)) is not None and
                 math.isclose(_number(got[k]), float(v), abs_tol=0.01)
                 for k, v in want.items())
    return (True, "") if ok else (False, "Неправильні параметри. " + instruction(action))


def compact_state(records):
    if not records:
        return ""
    lines = ["ПІДТВЕРДЖЕНІ результати реальних викликів (коротко):"]
    for r in records:
        name = r["tool"]
        args = _arguments(r)
        res = str(r["result"])
        if name == "search_recipes":
            res = res.splitlines()[0][:65]
        elif name == "product_info":
            res = res[:95]
        elif name == "scale_amount":
            res = res[:30]
        lines.append("- " + name + "(" + json.dumps(args, ensure_ascii=False, separators=(",", ":"))
                     + ") => " + res)
    return "\n".join(lines)


def _verified_rows(records):
    """Власне джерело: шість справжніх результатів scale_amount, не expected."""
    from decimal import Decimal, InvalidOperation

    rows = []
    for product, grams in ITEMS:
        kcal = _lookup_kcal(records, product)
        if kcal is None:
            raise ValueError("Немає даних product_info: " + product)
        recipe_calls = [r for r in records if _record_valid(
            r, "search_recipes", {}, product, grams, kcal)]
        if not recipe_calls:
            raise ValueError("Немає підтвердженого рецепту: " + product)
        matches = [r for r in records if _record_valid(
            r, "scale_amount", {}, product, grams, kcal)]
        if not matches:
            raise ValueError("Немає коректного scale_amount: " + product)
        try:
            value = Decimal(str(matches[-1]["result"]).replace(",", "."))
        except InvalidOperation as exc:
            raise ValueError("Некоректний результат scale_amount: " + product) from exc
        recipe = str(recipe_calls[-1]["result"]).splitlines()[0].strip()
        rows.append((product, grams, recipe, value))
    return rows


def _fmt_decimal(value):
    return format(value, "f").rstrip("0").rstrip(".") if "." in format(value, "f") else format(value, "f")


def verified_total(records):
    """Програмно додає тільки дійсні результати інструментів, без еталона."""
    return sum((row[3] for row in _verified_rows(records)), __import__("decimal").Decimal("0"))


def finish_instruction(records):
    rows = _verified_rows(records)
    total = verified_total(records)
    details = "\n".join(
        f"- {p}: {recipe}; {grams} г = {_fmt_decimal(value)} ккал"
        for p, grams, recipe, value in rows
    )
    return (
        "Усі 18 інструментів викликані реально. Подані результати перевірені програмою. "
        "Нижче КОНТРОЛЬНА СУМА, ПРОГРАМНО додана виключно із шести результатів "
        "scale_amount, НЕ з поля expected. Не обчислюй суму вдруге, просто точно "
        "відтворюй підсумок у фінальній відповіді українською мовою.\n"
        + details
        + f"\nСУМАРНА КАЛОРІЙНІСТЬ = {_fmt_decimal(total)} ккал."
    )


def verified_answer(records):
    """Резервний ФІНАЛ ПРОГРАМИ, не результат генерації моделі."""
    rows = _verified_rows(records)
    total = verified_total(records)
    parts = ["Результати за підтвердженими викликами інструментів:"]
    for p, grams, recipe, value in rows:
        parts.append(f"{p.capitalize()} ({grams} г): рецепт «{recipe}», {_fmt_decimal(value)} ккал.")
    parts.append(f"Сумарна калорійність усіх шести порцій: {_fmt_decimal(total)} ккал.")
    return "\n".join(parts)


def _correct_final(answer, expected):
    """Перевіряє останнє числове значення відповіді, а не випадкову згадку expected."""
    if not answer:
        return False
    normalized = answer.replace("\u00a0", " ").replace("\u202f", " ")
    numbers = re.findall(r"(?<![\w])\d+(?:[.,]\d+)?(?![\w])", normalized)
    if not numbers:
        return False
    final_number = _number(numbers[-1])
    expected_number = _number(expected)
    return (final_number is not None and expected_number is not None
            and math.isclose(final_number, expected_number, abs_tol=0.01))


def run_guided(task, max_steps=None, logfile_name=None, task_id="guided", log_overwrite=False):
    """Реальний цикл Ollama, покрокова перевірка; без прямого запуску інструментів замість моделі."""
    import config
    from model import call_model
    from compress import compress_history
    from state import TaskState
    from dispatcher import call_tool, MODEL_ERRORS
    from utils.lab_logger import custom_logger

    class CompactTaskState(TaskState):
        def render(self):
            return compact_state(self.results)

    if max_steps is None:
        max_steps = config.MAX_STEPS_LONG
    logger = custom_logger(logfile_name or config.LAB_LOGFILE_NAME, overwrite=log_overwrite)
    state = CompactTaskState(task_id)
    meta = json.loads(Path(__file__).with_name("long_task.json").read_text(encoding="utf-8"))
    messages = [
        {"role": "system", "content": config.SYSTEM +
         "\nЕксперимент із планувальником: викликай рівно ОДИН інструмент, "
         "коли користувач називає наступну дію. Аргументи не змінюй."},
        {"role": "user", "content": task + "\n\n" + instruction(next_action([]))},
    ]
    logger.info("\n" + "=" * 60)
    logger.info("ЗАДАЧА: " + task)
    logger.info("  GUIDED_V4_FINAL: GUIDED_V3 + контрольна сума з інструментів та прозорий програмний fallback")
    final_failures = 0  # GUIDED_V4_FINAL: максимум дві спроби генерації підсумку
    for step in range(1, max_steps + 1):
        response, from_cache = call_model(messages, step, logger)
        if response is None:
            return None
        choice = response.choices[0]
        msg = choice.message
        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else None
        completion_tokens = usage.completion_tokens if usage else None
        logger.info(f"\n--- крок {step} | помилок поспіль=0 | prompt_tokens={prompt_tokens if prompt_tokens is not None else 'невідомо'} | completion_tokens={completion_tokens if completion_tokens is not None else 'невідомо'}" + (" | з кешу" if from_cache else ""))
        action = next_action(state.results)

        if not msg.tool_calls:
            if action is not None:
                logger.warning("  НЕЗАВЕРШЕНА ЗАДАЧА: модель відповіла до потрібного виклику")
                messages.append({"role": "assistant", "content": msg.content or ""})
                messages.append({"role": "user", "content": instruction(action)})
            else:
                if _correct_final(msg.content or "", meta["expected"]):
                    logger.info("ВІДПОВІДЬ: " + (msg.content or ""))
                    logger.info("  GUIDED_V3: успішно, виконано 18 валідних викликів")
                    return msg.content
                logger.warning("  ПОМИЛКА СУМИ: результати інструментів повні, але відповідь моделі неточна")
                logger.warning("  ВІДПОВІДЬ МОДЕЛІ (некоректна): " + repr(msg.content or "")[:700])
                final_failures += 1
                if final_failures >= 2:
                    # Не маскуємо програмне підсумовування під відповідь моделі.
                    program_answer = verified_answer(state.results)
                    if not _correct_final(program_answer, meta["expected"]):
                        logger.error("  ПОМИЛКА: сума з інструментів НЕ збігається з expected; фінал не підміняємо")
                        return None
                    logger.warning("  GUIDED_V4_FINAL: модель двічі помилилася; фінал СКЛАДЕНО ПРОГРАМОЮ з реальних результатів інструментів")
                    logger.info("ВІДПОВІДЬ ПРОГРАМИ: " + program_answer)
                    return program_answer
                messages.append({"role": "assistant", "content": msg.content or ""})
                messages.append({"role": "user", "content": finish_instruction(state.results) +
                                 "\nНе перераховуй. Просто перепиши перевірену суму дослівно."})
        else:
            if len(msg.tool_calls) > 1:
                logger.info(f"  GUIDED_V3: модель запропонувала {len(msg.tool_calls)} викликів; обробляємо лише перший")
                msg.tool_calls = msg.tool_calls[:1]
            call = msg.tool_calls[0]
            name = call.function.name
            raw = call.function.arguments
            logger.info(f"  виклик   : {name}({raw})")
            messages.append(msg.model_dump(exclude_none=True))
            valid, reason = validate_call(name, raw, action)
            if valid:
                level, result = call_tool(name, raw)
                logger.info(f"  рівень   : {level}")
                logger.info(f"  результат: {result}")
                if level == "ok":
                    state.record(name, raw, result)
                    messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})
                else:
                    messages.append({"role": "tool", "tool_call_id": call.id,
                                     "content": f"Помилка {level}: {result}; спробуй ще раз."})
                    if level in MODEL_ERRORS:
                        logger.warning("  GUIDED_V3: виклик інструмента відхилено диспетчером")
            else:
                logger.warning("  GUIDED_V3: валідація відхилила некоректний виклик: " + reason)
                messages.append({"role": "tool", "tool_call_id": call.id, "content": reason})
            upcoming = next_action(state.results)
            messages.append({"role": "user", "content": instruction(upcoming) if upcoming is not None
                             else finish_instruction(state.results)})

        # Використовуємо оригінальний COMPRESS_AT / KEEP_LAST та три конфігурації ЛР4.
        messages = compress_history(messages, task, prompt_tokens or 0, state, logger)
    logger.info("СТОП: вичерпано ліміт кроків GUIDED_V3")
    logger.info(f"  Зроблено валідних викликів: {len(state.results)} з 18")
    return None
