
import json
import re
import math

from langfuse import observe

import config
from model import call_model
from compress import compress_history
from state import TaskState
from dispatcher import call_tool, check_response, MODEL_ERRORS
from utils.lab_logger import custom_logger


REQUIRED_PRODUCTS = [
    ("рис", 300),
    ("куряче філе", 500),
    ("твердий сир", 150),
    ("вівсяні пластівці", 100),
    ("макарони", 200),
    ("помідори", 250),
]


def extract_kcal(result):
    """Витягує калорійність із відповіді product_info."""
    match = re.search(
        r"Калорійність:\s*([\d.,]+)\s*ккал",
        str(result),
        re.IGNORECASE,
    )

    if not match:
        return None

    return float(match.group(1).replace(",", "."))


def parse_arguments(args_raw):
    """Безпечно розбирає аргументи виклику інструмента."""
    try:
        result = json.loads(args_raw)
        return result if isinstance(result, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def expected_instruction(operation, product, grams, pending_kcal):
    """Формує інструкцію для наступного обов'язкового виклику."""
    if operation == "search_recipes":
        return f"Виконай search_recipes з query='{product}'."

    if operation == "product_info":
        return f"Виконай product_info з product='{product}'."

    return (
        f"Виконай scale_amount для продукту {product}: "
        f"amount={pending_kcal}, base_servings=100, "
        f"target_servings={grams}."
    )


def build_final_answer(results):
    """Формує фінальну відповідь на основі результатів інструментів."""
    total = sum(item[2] for item in results)

    lines = ["Розрахунок калорійності шести продуктів:"]

    for product, grams, kcal in results:
        lines.append(
            f"- {product}: {grams} г — {kcal:g} ккал"
        )

    lines.append(f"Загальна калорійність: {total:g} ккал")

    return "\n".join(lines)


@observe()
def run_agent(
    task,
    max_steps=None,
    logfile_name=config.LAB_LOGFILE_NAME,
    task_id="task",
    log_overwrite=False,
    min_tool_calls=0,
):
    """Виконує завдання та повертає текст відповіді або None."""

    max_steps = max_steps or config.MAX_STEPS

    logger = custom_logger(
        logfile_name,
        f"logs/{logfile_name}.log",
        overwrite=log_overwrite,
    )

    messages = [
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    retries = 0
    successful_tool_calls = 0
    state = TaskState(task_id)

    pending_kcal = None
    pending_product = None


    strict_plan = min_tool_calls >= 18

    required_sequence = []

    if strict_plan:
        for product, grams in REQUIRED_PRODUCTS:
            required_sequence.extend([
                ("search_recipes", product, grams),
                ("product_info", product, grams),
                ("scale_amount", product, grams),
            ])

    expected_index = 0
    calculated_results = []

    logger.info(f"ЗАДАЧА: {task}")

    if strict_plan:
        logger.info(
            f"Увімкнено строгий план: "
            f"{len(required_sequence)} обов'язкових викликів."
        )

    for step in range(1, max_steps + 1):
        tool_choice = None

        if strict_plan and expected_index < len(required_sequence):
            operation, product, grams = required_sequence[expected_index]
            tool_choice = {
                "type": "function",
                "function": {"name": operation},
            }

        response, from_cache = call_model(
            messages, step, logger, tool_choice=tool_choice
        )

        if response is None:
            return None

        usage = getattr(response, "usage", None)
        prompt_tokens = getattr(usage, "prompt_tokens", 0)
        completion_tokens = getattr(usage, "completion_tokens", 0)

        logger.info(
            f"\n--- крок {step} | prompt_tokens={prompt_tokens} "
            f"| completion_tokens={completion_tokens}"
            + (" | з кешу" if from_cache else "")
        )

        response_error = check_response(response)

        if response_error:
            level, error_text = response_error
            retries += 1

            logger.warning(
                f"Помилка відповіді моделі | level={level} "
                f"| retries={retries} | message={error_text}"
            )

            if retries > config.MAX_RETRIES:
                return "Перевищено ліміт повторних спроб. " + error_text

            messages.append({
                "role": "user",
                "content": (
                    "Попередня відповідь була некоректною: "
                    + error_text
                    + " Спробуй ще раз."
                ),
            })
            continue

        message = response.choices[0].message
        used = prompt_tokens

        # Обробка фінальної відповіді моделі.
        if not message.tool_calls:
            answer = (message.content or "").strip()

            if not answer:
                logger.warning("Модель повернула порожню відповідь.")
                return None
            if strict_plan and expected_index < len(required_sequence):
                operation, product, grams = required_sequence[expected_index]

                instruction = expected_instruction(
                    operation,
                    product,
                    grams,
                    pending_kcal,
                )

                logger.warning(
                    f"Передчасна фінальна відповідь. "
                    f"Виконано {expected_index}/"
                    f"{len(required_sequence)} операцій. "
                    f"Наступна операція: {operation}, продукт: {product}."
                )

                messages.append({
                    "role": "assistant",
                    "content": answer,
                })

                messages.append({
                    "role": "user",
                    "content": (
                        "Завдання ще не завершене. "
                        f"Виконано {expected_index}/"
                        f"{len(required_sequence)} обов'язкових операцій. "
                        f"Наступна операція: {instruction} "
                        "Виконай саме її. Не пропускай інструменти, "
                        "не додавай інші продукти та не переходь "
                        "до наступного продукту передчасно."
                    ),
                })
                continue

            if successful_tool_calls < min_tool_calls:
                remaining = min_tool_calls - successful_tool_calls

                logger.warning(
                    f"Недостатньо успішних викликів: "
                    f"{successful_tool_calls}/{min_tool_calls}."
                )

                messages.append({
                    "role": "assistant",
                    "content": answer,
                })

                messages.append({
                    "role": "user",
                    "content": (
                        f"Потрібно виконати ще {remaining} успішних "
                        "викликів інструментів. Продовжуй роботу."
                    ),
                })
                continue

            logger.info(f"ВІДПОВІДЬ: {answer}")
            return answer


        call = message.tool_calls[0]
        name = call.function.name
        args_raw = call.function.arguments
        args = parse_arguments(args_raw)

        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [{
                "id": call.id,
                "type": "function",
                "function": {
                    "name": name,
                    "arguments": args_raw,
                },
            }],
        })

        plan_error = None

        if strict_plan:
            if expected_index >= len(required_sequence):
                plan_error = (
                    "Усі обов'язкові операції виконані. "
                    "Підготуй фінальну відповідь."
                )
            else:
                expected_name, expected_product, expected_grams = (
                    required_sequence[expected_index]
                )

                if name != expected_name:
                    plan_error = (
                        f"Порушено послідовність. "
                        f"Потрібен інструмент {expected_name} "
                        f"для продукту {expected_product}, "
                        f"а не {name}."
                    )

                elif name == "search_recipes":
                    query = str(args.get("query", "")).strip().casefold()

                    if query != expected_product.casefold():
                        plan_error = (
                            f"Неправильний продукт для пошуку. "
                            f"Потрібно: {expected_product}."
                        )

                elif name == "product_info":
                    product = str(
                        args.get("product", "")
                    ).strip().casefold()

                    if product != expected_product.casefold():
                        plan_error = (
                            f"Потрібно отримати інформацію саме про "
                            f"{expected_product}."
                        )

                elif name == "scale_amount":
                    try:
                        amount = float(args["amount"])
                        base = float(args["base_servings"])
                        target = float(args["target_servings"])
                    except (KeyError, TypeError, ValueError):
                        amount = None
                        base = None
                        target = None

                    if (
                        pending_kcal is None
                        or pending_product != expected_product
                    ):
                        plan_error = (
                            f"Спочатку виконай product_info "
                            f"для {expected_product}."
                        )

                    elif (
                        amount is None
                        or not math.isclose(
                            amount,
                            pending_kcal,
                            rel_tol=0,
                            abs_tol=0.000001,
                        )
                        or base != 100
                        or target != expected_grams
                    ):
                        plan_error = (
                            f"Неправильні параметри scale_amount "
                            f"для {expected_product}. "
                            f"Потрібно amount={pending_kcal}, "
                            f"base_servings=100, "
                            f"target_servings={expected_grams}."
                        )


        elif name == "scale_amount":
            try:
                amount = float(args["amount"])
            except (KeyError, TypeError, ValueError):
                amount = None

            if pending_kcal is None:
                plan_error = (
                    "Спочатку успішно виконай product_info."
                )

            elif (
                amount is None
                or not math.isclose(
                    amount,
                    pending_kcal,
                    rel_tol=0,
                    abs_tol=0.000001,
                )
                or args.get("base_servings") != 100
            ):
                plan_error = (
                    f"Неправильні параметри scale_amount. "
                    f"Потрібно amount={pending_kcal} "
                    f"та base_servings=100."
                )


        if plan_error:
            level = "meaning"
            result = plan_error
        else:
            level, result = call_tool(name, args_raw)


        if level == "ok" and name == "product_info":
            kcal = extract_kcal(result)

            if kcal is None:
                level = "meaning"
                result = (
                    "Не вдалося отримати числову калорійність "
                    "із відповіді product_info."
                )
            else:
                pending_kcal = kcal
                pending_product = args.get("product")

        logger.info(
            f"  виклик   : {name}({args_raw}) -> {result}"
        )

        if level in MODEL_ERRORS:
            retries += 1

            logger.warning(
                f"Помилка моделі | level={level} | retries={retries}"
            )

            if name == "product_info":
                pending_kcal = None
                pending_product = None

            if retries > config.MAX_RETRIES:
                return "Перевищено ліміт повторних спроб. " + str(result)

        elif level == "ok":
            retries = 0
            successful_tool_calls += 1

            state.record(name, args_raw, result)

            if strict_plan:
                expected_name, expected_product, expected_grams = (
                    required_sequence[expected_index]
                )

                expected_index += 1

                logger.info(
                    f"ПРОГРЕС ПЛАНУ: "
                    f"{expected_index}/{len(required_sequence)}"
                )


                if expected_name == "scale_amount":
                    try:
                        calculated_kcal = float(result)
                    except (TypeError, ValueError):
                        logger.error(
                            "Не вдалося зчитати результат scale_amount."
                        )
                        return None

                    calculated_results.append(
                        (
                            expected_product,
                            expected_grams,
                            calculated_kcal,
                        )
                    )

                    pending_kcal = None
                    pending_product = None


                if expected_index == len(required_sequence):
                    if len(calculated_results) != len(REQUIRED_PRODUCTS):
                        logger.error(
                            "Кількість результатів розрахунку неправильна."
                        )
                        return None

                    answer = build_final_answer(calculated_results)

                    logger.info(f"ВІДПОВІДЬ: {answer}")
                    return answer

        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": str(result),
        })

        messages = compress_history(
            messages,
            task,
            used,
            state,
            logger,
        )
        if strict_plan and expected_index < len(required_sequence):
            next_name, next_product, next_grams = (
                required_sequence[expected_index]
            )

            instruction = expected_instruction(
                next_name,
                next_product,
                next_grams,
                pending_kcal,
            )

            messages.append({
                "role": "user",
                "content": (
                    f"Наступний обов'язковий крок "
                    f"{expected_index + 1}/{len(required_sequence)}. "
                    f"{instruction} "
                    "Виконай саме цей виклик інструмента. "
                    "Не переходь до іншого продукту."
                ),
            })

    logger.warning(f"Досягнуто ліміт кроків ({max_steps}).")

    if strict_plan:
        logger.warning(
            f"Виконано {expected_index}/{len(required_sequence)} "
            f"обов'язкових операцій."
        )

    return None


if __name__ == "__main__":
    print(run_agent("Знайди щось із куркою"))
