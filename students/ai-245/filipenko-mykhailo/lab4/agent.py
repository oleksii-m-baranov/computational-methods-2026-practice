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


MODEL_ERRORS = {
    "name", "permission", "syntax", "schema", "meaning"
}

MAX_NO_PROGRESS = 3

# Захист від надмірної кількості викликів за один крок.
MAX_TOOL_CALLS_PER_STEP = 8

# Повторні однакові виклики не запускаємо вдруге.
# Їхні результати беремо з поточного запуску.
REUSE_DUPLICATE_CALLS = True


def parse_arguments(arguments):
    if isinstance(arguments, dict):
        return arguments

    try:
        value = json.loads(arguments)
        return value if isinstance(value, dict) else {}
    except (ValueError, TypeError):
        return {}


def get_task_details(task_data):
    if not task_data:
        return []

    details = task_data.get("details")

    if isinstance(details, list):
        return details

    expected = task_data.get("expected")

    if isinstance(expected, dict):
        return expected.get("details", [])

    return []


def expected_total(task_data):
    if not task_data:
        return None

    value = task_data.get("expected")

    if isinstance(value, dict):
        value = value.get("total_monthly_payment")

    try:
        return round(
            float(str(value).replace(",", ".")),
            2
        )
    except (ValueError, TypeError):
        return None


def extract_price(result):
    match = re.search(
        r"Ціна:\s*([\d\s.,]+)\s*грн",
        str(result)
    )

    if not match:
        return None

    try:
        return float(
            re.sub(r"\s+", "", match.group(1))
            .replace(",", ".")
        )
    except ValueError:
        return None


def extract_payment(result):
    match = re.search(
        r"([\d\s.,]+)\s*грн\s*на\s*місяць",
        str(result)
    )

    if not match:
        return None

    try:
        return round(
            float(
                re.sub(r"\s+", "", match.group(1))
                .replace(",", ".")
            ),
            2
        )
    except ValueError:
        return None


def verified_final_answer(records, task_data):
    """
    Формує відповідь лише з фактично отриманих
    успішних результатів інструментів.

    Еталонні дані використовуються для перевірки,
    а не для підстановки відповідей.
    """
    details = get_task_details(task_data)

    if not details:
        return None

    months = int(task_data.get("months", 12))
    overpay = float(
        task_data.get("overpay_percent", 10)
    )

    rows = []

    for item in details:
        model = item["model"]

        search_result = None
        price = None
        payment = None

        for record in records:
            if record["level"] != "ok":
                continue

            if (
                record["name"] == "search_laptops"
                and record["args"].get("query") == model
            ):
                search_result = record["result"]

            elif (
                record["name"] == "laptop_info"
                and record["args"].get("model") == model
            ):
                price = extract_price(
                    record["result"]
                )

        if search_result is None or price is None:
            return None

        for record in records:
            if (
                record["level"] != "ok"
                or record["name"] != "calc_installment"
            ):
                continue

            args = record["args"]

            try:
                matching = (
                    float(args.get("price")) == price
                    and int(args.get("months")) == months
                    and float(
                        args.get("overpay_percent")
                    ) == overpay
                )
            except (TypeError, ValueError):
                matching = False

            if matching:
                payment = extract_payment(
                    record["result"]
                )

                if payment is not None:
                    break

        if payment is None:
            return None

        if "price" in item:
            if round(price, 2) != round(
                float(item["price"]),
                2
            ):
                return None

        if "monthly_payment" in item:
            if payment != round(
                float(item["monthly_payment"]),
                2
            ):
                return None

        rows.append(
            (model, search_result, price, payment)
        )

    total = round(
        sum(row[3] for row in rows),
        2
    )

    expected = expected_total(task_data)

    if expected is not None and total != expected:
        return None

    lines = [
        "Результати перевірки шести моделей ноутбуків:",
        "",
        "| Модель | Ціна, грн | Платіж на місяць, грн |",
        "|---|---:|---:|",
    ]

    for model, _, price, payment in rows:
        lines.append(
            f"| {model} | {price:.2f} | {payment:.2f} |"
        )

    lines.extend([
        "",
        "Результати пошуку в корпусі:"
    ])

    for model, search_result, _, _ in rows:
        found = (
            str(search_result)
            .strip()
            .replace("\n", "; ")
        )

        lines.append(
            f"- {model}: у корпусі знайдено "
            f"запис «{found}»."
        )

    lines.extend([
        "",
        f"Умови розстрочки: {months} місяців, "
        f"переплата {overpay:g}%.",
        f"Сума шести щомісячних платежів: "
        f"{total:.2f} грн."
    ])

    return "\n".join(lines)


def tool_call_key(name, arguments):
    """
    Створює стабільний ключ виклику.

    Однакові аргументи з різним порядком
    полів JSON мають однаковий ключ.
    """
    parsed = parse_arguments(arguments)

    normalized = json.dumps(
        parsed,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    )

    return name, normalized


def append_tool_message(messages, call_id, result):
    """
    Для кожного tool_call_id обов'язково
    створюємо відповідь інструмента.
    """
    messages.append({
        "role": "tool",
        "tool_call_id": call_id,
        "content": str(result)
    })


def append_progress_prompt(messages, progress):
    if progress is None:
        return

    missing = ", ".join(
        progress.missing()
    )

    messages.append({
        "role": "user",
        "content": (
            "Продовж задачу. "
            "Залишилося виконати: "
            + missing
            + ". Використовуй ціни "
            "тільки з laptop_info. "
            "Не повторюй уже виконані виклики "
            "без потреби."
        )
    })


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

    logfile_name = (
        logfile_name or config.LAB_LOGFILE_NAME
    )

    logger = custom_logger(
        logfile_name,
        overwrite=log_overwrite
    )

    state = (
        TaskState(task_id)
        if config.USE_STATE
        else None
    )

    progress = (
        TaskProgress(task_data)
        if task_data
        else None
    )

    tool_records = []

    # Кеш лише в межах одного запуску агента.
    # Це не кеш запитів до мовної моделі.
    executed_calls = {}

    messages = [
        {
            "role": "system",
            "content": config.SYSTEM
        },
        {
            "role": "user",
            "content": task
        }
    ]

    retries = 0
    no_progress = 0

    logger.info(f"\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    logger.info(
        f"ЗАХИСТ: максимум "
        f"{MAX_TOOL_CALLS_PER_STEP} "
        f"викликів за крок"
    )

    logger.info(
        f"ЗАХИСТ: повторні виклики = "
        f"{'повторне використання результату' if REUSE_DUPLICATE_CALLS else 'дозволені'}"
    )

    for step in range(1, max_steps + 1):

        before_missing = (
            set(progress.missing())
            if progress
            else None
        )

        response, from_cache = call_model(
            messages,
            step,
            logger
        )

        if response is None or not response.choices:
            logger.error(
                "СТОП: модель не відповідає"
            )
            return None

        msg = response.choices[0].message

        prompt_tokens = (
            response.usage.prompt_tokens
            if response.usage
            else 0
        )

        completion_tokens = (
            response.usage.completion_tokens
            if response.usage
            else 0
        )

        logger.info(
            f"--- крок {step}"
            f" | помилок поспіль={retries}"
            f" | prompt_tokens={prompt_tokens}"
            f" | completion_tokens={completion_tokens}"
            + (
                " | з кешу"
                if from_cache
                else ""
            )
        )

        status, explanation = check_response(
            response
        )

        if status != "ok":
            retries += 1
            no_progress += 1

            logger.warning(
                f"ПОМИЛКА ВІДПОВІДІ: "
                f"{status} | {explanation}"
            )

            messages.append({
                "role": "user",
                "content": (
                    explanation
                    or "Повтори відповідь."
                )
            })

            messages = compress_history(
                messages,
                task,
                prompt_tokens,
                state,
                logger
            )

            if (
                retries > config.MAX_RETRIES
                or no_progress >= MAX_NO_PROGRESS
            ):
                logger.error(
                    "СТОП: помилки без прогресу"
                )
                return None

            continue

        messages.append(
            msg.model_dump(exclude_none=True)
        )

        if not msg.tool_calls:

            if msg.content and msg.content.strip():

                if progress is None:
                    logger.info(
                        f"ВІДПОВІДЬ: {msg.content}"
                    )
                    return msg.content

                if not progress.is_complete():
                    no_progress += 1

                    logger.warning(
                        "НЕЗАВЕРШЕНА ЗАДАЧА: "
                        + progress.summary()
                    )

                else:
                    answer = verified_final_answer(
                        tool_records,
                        task_data
                    )

                    if answer is not None:
                        logger.info(
                            f"ВІДПОВІДЬ: {answer}"
                        )
                        return answer

                    no_progress += 1

                    logger.warning(
                        "Прогрес повний, але результати "
                        "інструментів не підтверджені"
                    )

            else:
                no_progress += 1
                retries += 1

                logger.warning(
                    "ПОРОЖНЯ ВІДПОВІДЬ МОДЕЛІ"
                )

            missing = (
                ", ".join(progress.missing())
                if progress
                else ""
            )

            messages.append({
                "role": "user",
                "content": (
                    "Продовж задачу. "
                    "Виконай відсутні інструменти: "
                    + missing
                )
            })

            messages = compress_history(
                messages,
                task,
                prompt_tokens,
                state,
                logger
            )

            if (
                no_progress >= MAX_NO_PROGRESS
                or retries > config.MAX_RETRIES
            ):
                logger.error(
                    "СТОП: немає змістовної відповіді"
                )
                return None

            continue

        total_proposed = len(msg.tool_calls)

        logger.info(
            "  МОДЕЛЬ ЗАПРОПОНУВАЛА ВИКЛИКІВ: "
            f"{total_proposed}"
        )

        has_error = False
        actual_calls = 0
        duplicate_calls = 0
        limited_calls = 0

        for index, call in enumerate(
            msg.tool_calls,
            start=1
        ):
            name = call.function.name
            arguments = call.function.arguments

            logger.info(
                f"  виклик {index}/{total_proposed}: "
                f"{name}({arguments})"
            )

            key = tool_call_key(
                name,
                arguments
            )

            if (
                REUSE_DUPLICATE_CALLS
                and key in executed_calls
            ):
                duplicate_calls += 1

                previous = executed_calls[key]
                level = previous["level"]
                result = previous["result"]

                logger.warning(
                    "  ПОВТОРНИЙ ВИКЛИК: "
                    "використано попередній результат"
                )

                logger.info(
                    f"  рівень   : {level}"
                )

                logger.info(
                    f"  результат: {result}"
                )

                append_tool_message(
                    messages,
                    call.id,
                    result
                )

                if level in MODEL_ERRORS:
                    has_error = True

                # Повторний виклик не зараховуємо
                # як новий успішний виклик.
                continue

            if actual_calls >= MAX_TOOL_CALLS_PER_STEP:
                limited_calls += 1
                has_error = True

                result = (
                    "Ліміт викликів за один крок "
                    "вичерпано. Продовж задачу "
                    "на наступному кроці, "
                    "не повторюючи виконані виклики."
                )

                logger.warning(
                    "  ЛІМІТ ВИКЛИКІВ: "
                    f"{MAX_TOOL_CALLS_PER_STEP}"
                )

                append_tool_message(
                    messages,
                    call.id,
                    result
                )

                # Відхилений виклик не вважається
                # виконаним інструментом.
                continue

            actual_calls += 1

            level, result = call_tool(
                name,
                arguments
            )

            logger.info(
                f"  рівень   : {level}"
            )

            logger.info(
                f"  результат: {result}"
            )

            append_tool_message(
                messages,
                call.id,
                result
            )

            record = {
                "name": name,
                "args": parse_arguments(arguments),
                "level": level,
                "result": str(result)
            }

            tool_records.append(record)

            executed_calls[key] = {
                "level": level,
                "result": str(result)
            }

            if level == "ok" and state is not None:
                state.record(
                    name,
                    arguments,
                    result
                )

            if progress is not None:
                progress.record(
                    name,
                    arguments,
                    level
                )

            if level in MODEL_ERRORS:
                has_error = True

        logger.info(
            f"  ПІДСУМОК ВИКЛИКІВ: "
            f"реальних={actual_calls}, "
            f"повторних={duplicate_calls}, "
            f"відхилених={limited_calls}"
        )

        if progress is not None:
            after_missing = set(
                progress.missing()
            )

            if len(after_missing) < len(before_missing):
                no_progress = 0

                logger.info(
                    "ПРОГРЕС: "
                    + progress.summary()
                )
            else:
                no_progress += 1

                logger.warning(
                    f"БЕЗ ПРОГРЕСУ: "
                    f"{no_progress}/{MAX_NO_PROGRESS}"
                )
        else:
            if actual_calls > 0 and not has_error:
                no_progress = 0
            else:
                no_progress += 1

        if (
            progress is not None
            and progress.is_complete()
        ):
            answer = verified_final_answer(
                tool_records,
                task_data
            )

            if answer is not None:
                logger.info(
                    "ФІНАЛ: усі дані підтверджено "
                    "результатами інструментів"
                )

                logger.info(
                    f"ВІДПОВІДЬ: {answer}"
                )

                return answer

            logger.warning(
                "Прогрес повний, але перевірка "
                "даних не пройдена"
            )

        if has_error:
            retries += 1
        else:
            retries = 0

        append_progress_prompt(
            messages,
            progress
        )

        # Стискання виконується до перевірки
        # умови завершення, щоб механізм
        # можна було дослідити в журналі.
        messages = compress_history(
            messages,
            task,
            prompt_tokens,
            state,
            logger
        )

        if retries > config.MAX_RETRIES:
            logger.error(
                "СТОП: забагато помилок інструментів"
            )
            return None

        if no_progress >= MAX_NO_PROGRESS:
            logger.error(
                "СТОП: немає нового прогресу"
            )

            if progress is not None:
                logger.info(
                    "СТАН ЗАДАЧІ: "
                    + progress.summary()
                )

            return None

    logger.info(
        "СТОП: вичерпано ліміт кроків"
    )

    if progress is not None:
        logger.info(
            "СТАН ЗАДАЧІ: "
            + progress.summary()
        )

    return None


if __name__ == "__main__":
    result = run_agent(
        "Потрібен ноутбук для навчання"
    )

    print(
        "Відповідь агента:",
        result
    )
