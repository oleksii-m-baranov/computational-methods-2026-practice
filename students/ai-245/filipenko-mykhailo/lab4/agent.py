import json
import re

from langfuse import observe

import config
from model import call_model
from dispatcher import call_tool, check_response
from compress import compress_history
from state import TaskState
from task_progress import TaskProgress
from utils.lab_logger import custom_logger


MODEL_ERRORS = {"name", "permission", "syntax", "schema", "meaning"}
MAX_NO_PROGRESS = 3
MAX_FINAL_ATTEMPTS = 3


def normalize_number(value):
    return re.sub(r"\s+", "", str(value)).replace(",", ".")


def contains_amount(text, amount):
    normalized = normalize_number(text)

    value = float(amount)
    whole = int(value)
    cents = round((value - whole) * 100)

    if cents == 0:
        pattern = rf"(?<![\d.]){whole}(?:\.0+)?(?![\d.])"
    else:
        pattern = rf"(?<![\d.]){whole}\.{cents:02d}(?!\d)"

    return re.search(pattern, normalized) is not None


def expected_total(task_data):
    if not task_data:
        return None

    expected = task_data.get("expected")

    try:
        if isinstance(expected, dict):
            return float(expected["total_monthly_payment"])

        return float(str(expected).replace(",", "."))

    except (ValueError, TypeError, KeyError):
        return None


def final_answer_is_complete(answer, task_data):
    if not answer:
        return False

    if not task_data:
        return bool(str(answer).strip())

    total = expected_total(task_data)

    if total is None or not contains_amount(answer, total):
        return False

    expected = task_data.get("expected", {})
    if not isinstance(expected, dict):
        return True

    details = expected.get("details", [])

    for item in details:
        model = item["model"]
        price = item["price"]
        monthly = item["monthly_payment"]

        if model not in answer:
            return False

        if not contains_amount(answer, price):
            return False

        if not contains_amount(answer, monthly):
            return False

    return True


def parse_arguments(arguments):
    try:
        if isinstance(arguments, dict):
            return arguments
        return json.loads(arguments)
    except (ValueError, TypeError):
        return {}


def build_tool_summary(tool_records, task_data):
    if not task_data:
        return ""

    expected = task_data.get("expected", {})
    if not isinstance(expected, dict):
        return ""

    details = expected.get("details", [])
    months = task_data.get("months", 12)
    overpay = task_data.get("overpay_percent", 10)

    lines = []
    total = 0.0

    for item in details:
        model = item["model"]

        price = None
        payment = None

        for record in tool_records:
            if record["level"] != "ok":
                continue

            if (
                record["name"] == "laptop_info"
                and record["args"].get("model") == model
            ):
                match = re.search(
                    r"Ціна:\s*([\d\s.,]+)\s*грн",
                    record["result"]
                )

                if match:
                    price = float(
                        normalize_number(match.group(1))
                    )

        if price is None:
            continue

        for record in tool_records:
            if (
                record["level"] == "ok"
                and record["name"] == "calc_installment"
            ):
                args = record["args"]

                try:
                    matches = (
                        float(args.get("price")) == price
                        and int(args.get("months")) == int(months)
                        and float(args.get("overpay_percent"))
                        == float(overpay)
                    )
                except (ValueError, TypeError):
                    matches = False

                if matches:
                    match = re.search(
                        r"([\d\s.,]+)\s*грн\s*на\s*місяць",
                        record["result"]
                    )

                    if match:
                        payment = float(
                            normalize_number(match.group(1))
                        )
                        break

        if payment is not None:
            total += payment
            lines.append(
                f"{model}: ціна {price:.2f} грн, "
                f"платіж {payment:.2f} грн/міс."
            )

    if len(lines) != len(details):
        return (
            "Не всі результати інструментів знайдено. "
            "Не вигадуй відсутні дані.\n"
            + "\n".join(lines)
        )

    return (
        "ПЕРЕВІРЕНІ РЕЗУЛЬТАТИ ІНСТРУМЕНТІВ:\n"
        + "\n".join(lines)
        + f"\nСума шести платежів: {total:.2f} грн/міс.\n"
        + "Сформуй фінальну таблицю з цих результатів."
    )


def make_final_instruction(task_data, progress, tool_records):
    summary = build_tool_summary(tool_records, task_data)

    instruction = (
        "Усі необхідні виклики інструментів завершено. "
        "Сформуй остаточну відповідь українською мовою. "
        "Не викликай інструменти повторно. "
        "Не пиши, що продовжиш роботу. "
        "Наведи таблицю з назвами моделей, цінами "
        "та щомісячними платежами. "
        "Наприкінці вкажи загальну суму платежів.\n\n"
        + summary
    )

    if progress is not None:
        instruction += "\n" + progress.summary()

    return instruction


@observe()
def run_agent(
    task,
    max_steps=None,
    logfile_name=None,
    task_id="task",
    log_overwrite=False,
    task_data=None
):
    max_steps = max_steps or config.MAX_STEPS
    logfile_name = logfile_name or config.LAB_LOGFILE_NAME

    logger = custom_logger(
        logfile_name,
        overwrite=log_overwrite
    )

    state = TaskState(task_id) if config.USE_STATE else None
    progress = TaskProgress(task_data) if task_data else None

    tool_records = []

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task}
    ]

    retries = 0
    no_progress = 0
    final_attempts = 0

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, max_steps + 1):
        before_missing = (
            set(progress.missing())
            if progress is not None else None
        )

        response, from_cache = call_model(
            messages,
            step,
            logger
        )

        if response is None or not response.choices:
            logger.error("СТОП: модель не відповідає")
            return None

        msg = response.choices[0].message

        prompt_tokens = (
            response.usage.prompt_tokens
            if response.usage else 0
        )

        completion_tokens = (
            response.usage.completion_tokens
            if response.usage else 0
        )

        logger.info(
            f"--- крок {step}"
            f" | помилок поспіль={retries}"
            f" | prompt_tokens={prompt_tokens}"
            f" | completion_tokens={completion_tokens}"
            + (" | з кешу" if from_cache else "")
        )

        status, explanation = check_response(response)

        if status != "ok":
            retries += 1
            no_progress += 1

            logger.warning(
                f"ПОМИЛКА ВІДПОВІДІ: {status} | {explanation}"
            )

            if (
                retries > config.MAX_RETRIES
                or no_progress >= MAX_NO_PROGRESS
            ):
                logger.error("СТОП: помилки без прогресу")
                return None

            messages.append({
                "role": "user",
                "content": explanation or "Повтори відповідь."
            })

            messages = compress_history(
                messages, task, prompt_tokens, state, logger
            )
            continue

        messages.append(msg.model_dump(exclude_none=True))

        if not msg.tool_calls:
            if msg.content and msg.content.strip():

                if progress is not None and not progress.is_complete():
                    no_progress += 1

                    logger.warning(
                        "НЕЗАВЕРШЕНА ЗАДАЧА: "
                        + progress.summary()
                    )

                    if no_progress >= MAX_NO_PROGRESS:
                        logger.error(
                            "СТОП: три кроки без прогресу"
                        )
                        return None

                    messages.append({
                        "role": "user",
                        "content": (
                            "Задача ще не завершена. "
                            "Виконай відсутні інструменти: "
                            + ", ".join(progress.missing())
                        )
                    })

                    messages = compress_history(
                        messages, task, prompt_tokens, state, logger
                    )
                    continue

                if progress is not None and progress.is_complete():
                    if not final_answer_is_complete(
                        msg.content, task_data
                    ):
                        final_attempts += 1

                        logger.warning(
                            "НЕПОВНА ФІНАЛЬНА ВІДПОВІДЬ: "
                            f"{final_attempts}/{MAX_FINAL_ATTEMPTS}"
                        )

                        if final_attempts >= MAX_FINAL_ATTEMPTS:
                            logger.error(
                                "СТОП: модель не сформувала "
                                "повну відповідь"
                            )
                            return None

                        messages.append({
                            "role": "user",
                            "content": make_final_instruction(
                                task_data,
                                progress,
                                tool_records
                            )
                        })

                        messages = compress_history(
                            messages, task, prompt_tokens, state, logger
                        )
                        continue

                logger.info(f"ВІДПОВІДЬ: {msg.content}")
                return msg.content

            retries += 1
            no_progress += 1

            if (
                retries > config.MAX_RETRIES
                or no_progress >= MAX_NO_PROGRESS
            ):
                logger.error("СТОП: немає змістовної відповіді")
                return None

            messages.append({
                "role": "user",
                "content": "Продовж виконання задачі."
            })

            messages = compress_history(
                messages, task, prompt_tokens, state, logger
            )
            continue

        logger.info(
            "  МОДЕЛЬ ЗАПРОПОНУВАЛА ВИКЛИКІВ: "
            f"{len(msg.tool_calls)}"
        )

        has_error = False

        for call in msg.tool_calls:
            name = call.function.name
            arguments = call.function.arguments

            logger.info(f"  виклик   : {name}({arguments})")

            level, result = call_tool(name, arguments)

            logger.info(f"  рівень   : {level}")
            logger.info(f"  результат: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result)
            })

            tool_records.append({
                "name": name,
                "args": parse_arguments(arguments),
                "level": level,
                "result": str(result)
            })

            if level == "ok" and state is not None:
                state.record(name, arguments, result)

            if progress is not None:
                progress.record(name, arguments, level)

            if level in MODEL_ERRORS:
                has_error = True

        if progress is not None:
            after_missing = set(progress.missing())

            if len(after_missing) < len(before_missing):
                no_progress = 0
                logger.info(
                    "ПРОГРЕС: " + progress.summary()
                )
            else:
                no_progress += 1
                logger.warning(
                    f"БЕЗ ПРОГРЕСУ: "
                    f"{no_progress}/{MAX_NO_PROGRESS}"
                )
        else:
            no_progress = 0

        if has_error:
            retries += 1
        else:
            retries = 0

        if retries > config.MAX_RETRIES:
            logger.error(
                "СТОП: забагато помилок інструментів"
            )
            return None

        if no_progress >= MAX_NO_PROGRESS:
            logger.error("СТОП: немає нового прогресу")

            if progress is not None:
                logger.info(
                    "СТАН ЗАДАЧІ: " + progress.summary()
                )

            return None

        if progress is not None:
            if progress.is_complete():
                messages.append({
                    "role": "user",
                    "content": make_final_instruction(
                        task_data,
                        progress,
                        tool_records
                    )
                })
            else:
                messages.append({
                    "role": "user",
                    "content": (
                        "Продовж задачу. "
                        "Залишилося виконати: "
                        + ", ".join(progress.missing())
                        + ". Використовуй ціни тільки з laptop_info."
                    )
                })

        messages = compress_history(
            messages, task, prompt_tokens, state, logger
        )

    logger.info("СТОП: вичерпано ліміт кроків")

    if progress is not None:
        logger.info(
            "СТАН ЗАДАЧІ: " + progress.summary()
        )

    return None


if __name__ == "__main__":
    result = run_agent(
        "Потрібен ноутбук для навчання"
    )
    print("Відповідь агента:", result)
