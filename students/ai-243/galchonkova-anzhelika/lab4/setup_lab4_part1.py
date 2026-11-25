import os
import subprocess
import sys

# 1. Створюємо data/corpus (12 файлів) та data/fertilizer.csv (16 рядків)
os.makedirs("data/corpus", exist_ok=True)
os.makedirs("logs", exist_ok=True)

plants = {
    "p01.txt": """Фікус Бенджаміна
Розсіяне світло, полив помірний, раз на 5-7 днів.
Жовтіє листя при надмірному поливі або холодних протягах.
Не переносить частих перестановок, реагує різким опаданням листя.""",

    "p02.txt": """Фікус Лірата
Яскраве розсіяне світло, полив помірний після просихання верхнього шару ґрунту.
При сухому повітрі в опалювальний сезон у рослини сохнуть кінчики великих листків.
Якщо в горщику застоюється вода, з'являються бурі плями та жовтіє листя.""",

    "p03.txt": """Заміокулькас
Півтінь або розсіяне світло, полив рідкісний, раз на 2-3 тижні.
Надмірна волога призводить до загнивання бульб, через що жовтіє листя.
Добре переносить сухе повітря квартир і не потребує частого обприскування.""",

    "p04.txt": """Монстера Деліціоза
Розсіяне світло або легка півтінь, полив регулярний у теплу пору року.
При нестачі вологи в повітрі сохнуть кінчики та краї листових пластин.
У глибокій тіні нове листя росте дрібним і без характерних розрізів.""",

    "p05.txt": """Спатифілум
Тінь або розсіяне світло, рясний полив м'якою відстояною водою.
При пересиханні ґрунту листя миттєво втрачає пружність і поникає.
Через сухе повітря або надлишок добрив у рослини сохнуть кінчики листків.""",

    "p06.txt": """Сансевієрія Триканта
Пряме сонце або півтінь, полив скупий, раз на 14-20 днів.
Потрапляння води в центр розетки спричиняє загнивання основи листя.
При тривалому перезволоженні листя стає м'яким і лягає на край горщика.""",

    "p07.txt": """Хлорофітум Чубатий
Розсіяне світло або півтінь, помірний полив двічі на тиждень влітку.
При нестачі освітлення смугасте листя блідне і втрачає декоративність.
Від жорсткої водопровідної води та сухості повітря сохнуть кінчики листків.""",

    "p08.txt": """Драцена Маргіната
Яскраве розсіяне світло, помірний полив без застою води в піддоні.
Нижнє листя природно старіє, але масове опадання листя свідчить про переохолодження.
При низькій вологості повітря та протягах у драцени сохнуть кінчики.""",

    "p09.txt": """Пеларгонія Зональна
Пряме сонце на південному вікні, помірний полив після підсихання ґрунту.
У тіні пагони витягуються, а цвітіння повністю припиняється.
При перезволоженні в прохолодну погоду жовтіє листя біля основи стебла.""",

    "p10.txt": """Алое Вера
Пряме сонце, рідкісний полив раз на 10-14 днів теплою водою.
При нестачі світла листя стає тонким, блідим і витягується вгору.
Надмірний полив узимку викликає кореневу гниль і розм'якшення стебла.""",

    "p11.txt": """Антуріум Андре
Розсіяне світло без прямих сонячних променів, регулярний полив теплою водою.
Полив холодною водою призводить до появи темних плям та опадання листя.
Потребує високої вологості повітря та пухкого повітропроникного субстрату.""",

    "p12.txt": """Калатея Медальйон
Тінь або м'яке розсіяне світло, регулярний полив відстояною водою.
На прямому сонці листя вигорає, скручується і вкривається сухими плямами.
При сухому повітрі швидко сохнуть кінчики та краї декоративних листків."""
}

for filename, content in plants.items():
    with open(f"data/corpus/{filename}", "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

csv_content = """plant,season,dose_ml_per_liter,frequency_days
Фікус Бенджаміна,весна,5,14
Фікус Лірата,весна,6,14
Заміокулькас,літо,3,30
Монстера Деліціоза,літо,7,14
Спатифілум,весна,4,14
Сансевієрія Триканта,зима,0,30
Хлорофітум Чубатий,літо,4,7
Драцена Маргіната,весна,5,21
Пеларгонія Зональна,літо,8,7
Алое Вера,літо,2,30
Антуріум Андре,весна,6,14
Орхідея Фаленопсис,весна,3,21
Гібіскус Китайський,літо,9,7
Бегонія Королівська,весна,5,14
Шефлера Деревовидна,осінь,4,21
Кротон Строкатий,літо,6,14
"""
with open("data/fertilizer.csv", "w", encoding="utf-8") as f:
    f.write(csv_content.strip() + "\n")

# 2. Створюємо .env з ключами Langfuse
env_text = """LANGFUSE_PUBLIC_KEY=pk-lf-0906379f-43de-4693-8161-c10aea2727f2
LANGFUSE_SECRET_KEY=sk-lf-b18493f6-36d8-4e00-a346-fe5d0f27348c
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_BASE_URL=https://cloud.langfuse.com
"""
with open(".env", "w", encoding="utf-8") as f:
    f.write(env_text)

# 3. Створюємо Modelfile для вузького вікна 4096
with open("Modelfile", "w", encoding="utf-8") as f:
    f.write("FROM qwen2.5:3b\nPARAMETER num_ctx 4096\n")

# 4. Усі файли для кроків 1-4 лабораторної роботи № 4
files = {
    "config.py": '''"""Налаштування агента."""
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:11434/v1"
API_KEY = "ollama"

MODEL = "qwen25-4k"
MAX_STEPS = 6
TEMPERATURE = 0.2

MAX_RETRIES = 2
ALLOWED = ["search_plants", "fertilizer_info", "calc_dose"]
RUN_TAG = "ctx-control"
LAB_LOGFILE_NAME = "lab4"

NUM_CTX = 4096
MAX_STEPS_LONG = 25

SYSTEM = """Ти консультант з догляду за кімнатними рослинами.
Не вигадуй дані — усе, чого не знаєш, дізнавайся інструментом.
Не рахуй самостійно, для цього є окремий інструмент.
Якщо потрібного інструмента немає, чесно скажи про це.
Коли даних достатньо, дай коротку відповідь українською."""
''',

    "tools.py": '''import csv
import os


def search_plants(query: str) -> str:
    q = query.lower()
    found = []
    folder = "data/corpus"
    for filename in sorted(os.listdir(folder)):
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            text = f.read().strip()
        if q in text.lower():
            found.append(text)
    if not found:
        return f"За запитом '{query}' нічого не знайдено."
    return "\\n---\\n".join(found)


def fertilizer_info(plant: str) -> str:
    with open("data/fertilizer.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["plant"].lower() == plant.lower():
                return (f"Доза: {row['dose_ml_per_liter']} мл на літр, "
                        f"періодичність: раз на "
                        f"{row['frequency_days']} днів")
    return f"Рослини '{plant}' немає в довіднику."


def calc_dose(pot_liters: float, dose_ml_per_liter: float) -> str:
    return f"{round(pot_liters * dose_ml_per_liter, 1)} мл"


def order_fertilizer(plant: str, liters: float) -> str:
    return f"Замовлено {liters} л добрива для '{plant}'"


TOOLS = {
    "search_plants": search_plants,
    "fertilizer_info": fertilizer_info,
    "calc_dose": calc_dose,
    "order_fertilizer": order_fertilizer,
}
''',

    "arguments.py": '''"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchPlantsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=2,
        max_length=50,
        description="Назва рослини, умова догляду або симптом, одне-два слова українською, не все питання користувача цілком",
    )


class FertilizerInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    plant: str = Field(
        min_length=2,
        max_length=60,
        description="Точна назва рослини, як вона записана в довіднику",
    )


class CalcDoseArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pot_liters: float = Field(
        gt=0,
        le=50,
        description="Об'єм горщика в літрах",
    )
    dose_ml_per_liter: float = Field(
        ge=0,
        le=50,
        description="Доза на літр, отримана з довідника",
    )


ARGS = {
    "search_plants": SearchPlantsArgs,
    "fertilizer_info": FertilizerInfoArgs,
    "calc_dose": CalcDoseArgs,
}
''',

    "schemas.py": '''"""Описи інструментів для моделі, згенеровані з класів аргументів."""
import config
from arguments import ARGS

DESCRIPTIONS = {
    "search_plants": "Шукає рослини за назвою, умовами догляду або симптомом проблеми. "
                   "Повертає картки знайдених рослин. "
                   "Використовуй, коли користувач описує рослину або проблему з нею.",
    "fertilizer_info": "Шукає рослину в довіднику підживлення та повертає дозу добрива на літр і періодичність у днях. "
                       "Використовуй, коли назва рослини вже відома, наприклад її щойно повернув search_plants.",
    "calc_dose": "Обчислює загальну кількість добрива в мілілітрах для горщика заданого об'єму. "
                 "Використовуй завжди, коли треба порахувати дозу; самостійно модель не рахує.",
}

SCHEMAS = []
for name in config.ALLOWED:
    SCHEMAS.append({
        "type": "function",
        "function": {
            "name": name,
            "description": DESCRIPTIONS[name],
            "parameters": ARGS[name].model_json_schema(),
        },
    })
''',

    "checks.py": '''"""Перевірки змісту аргументів."""
import csv

with open("data/fertilizer.csv", encoding="utf-8") as f:
    PLANTS = [row["plant"] for row in csv.DictReader(f)]


def check_meaning(name, args):
    if name == "fertilizer_info":
        if args.plant not in PLANTS:
            return (f"Помилка: рослини '{args.plant}' немає в довіднику підживлення. "
                    "Точну назву рослини можна дізнатися пошуком через інструмент search_plants. "
                    "Виклич search_plants або повідом користувачу, що даних про цю рослину немає.")
    if name == "calc_dose":
        if args.pot_liters * args.dose_ml_per_liter > 1000:
            return ("Помилка: загальна кількість добрива перевищує 1000 мл, що нереалістично для кімнатної рослини. "
                    "Перевір об'єм горщика та дозу на літр.")
    return None
''',

    "dispatcher.py": '''"""Перевірка і виконання виклику інструмента."""
from langfuse import observe
from pydantic import ValidationError

import config
from arguments import ARGS
from checks import check_meaning
from tools import TOOLS

MODEL_ERRORS = ["name", "permission", "syntax", "schema", "meaning"]


def format_validation_error(error):
    lines = ["Помилка: аргументи не пройшли перевірку."]
    for err in error.errors():
        if err["loc"]:
            field = err["loc"][0]
        else:
            field = "JSON"
        lines.append(f"Поле {field}: {err['msg']}")
    lines.append("Виправ аргументи і виклич інструмент ще раз.")
    return "\\n".join(lines)


@observe(name="call_tool")
def call_tool(name, args_raw):
    if name not in TOOLS:
        return "name", (f"Помилка: інструмента '{name}' не існує. "
                        f"Доступні: {', '.join(config.ALLOWED)}. "
                        "Виклич один з доступних або повідом користувачу, що такої дії немає.")

    if name not in config.ALLOWED:
        return "permission", (f"Помилка: інструмент '{name}' недоступний. "
                              "Не повторюй виклик, повідом користувачу, що ця дія недоступна.")

    try:
        args = ARGS[name].model_validate_json(args_raw)
    except ValidationError as error:
        level = "schema"
        for err in error.errors():
            if err["type"] == "json_invalid":
                level = "syntax"
        return level, format_validation_error(error)

    problem = check_meaning(name, args)
    if problem is not None:
        return "meaning", problem

    try:
        return "ok", str(TOOLS[name](**args.model_dump()))
    except Exception as error:
        return "tool", (f"Помилка: інструмент '{name}' зараз не працює ({error}). "
                        "Не повторюй виклик, повідом користувачу.")


def check_response(choice):
    if choice.finish_reason == "length":
        return "length", None

    msg = choice.message
    if not msg.tool_calls and msg.content:
        text = msg.content.strip()
        if "<tool_call>" in text or text.startswith("{"):
            return "syntax", ("Твоя відповідь схожа на виклик інструмента, але має неправильний формат. "
                              "Виклич інструмент ще раз через механізм інструментів "
                              "або дай відповідь користувачу звичайним текстом.")
    return None
''',

    "model.py": '''"""Виклик моделі. Тут же створюється клієнт, через який агент звертається до сервера."""
from langfuse.openai import OpenAI

import config
from schemas import SCHEMAS

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)


def call_model(messages, step, logger):
    """Один виклик моделі. Повертає пару (відповідь, чи_взято_з_кешу)."""
    try:
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            temperature=config.TEMPERATURE,
        )
        return response, False
    except Exception as error:
        logger.error(f"\\n--- крок {step} | ПОМИЛКА СЕРВЕРА: {error}")
        return None, False
''',

    "agent.py": '''"""Цикл агента з перевірками викликів."""
from langfuse import observe

import config
from model import call_model
from dispatcher import call_tool, check_response, MODEL_ERRORS
from utils.lab_logger import custom_logger


@observe()
def run_agent(task, max_steps=None, logfile_name=config.LAB_LOGFILE_NAME, log_overwrite=False):
    """task – питання користувача
    Повертає текст відповіді або None, якщо вичерпано ліміт."""
    max_steps = max_steps or config.MAX_STEPS
    logger = custom_logger(logfile_name, overwrite=log_overwrite)

    messages = [
        {"role": "system", "content": config.SYSTEM},
        {"role": "user", "content": task},
    ]
    retries = 0

    logger.info(f"\\n{'=' * 60}")
    logger.info(f"ЗАДАЧА: {task}")

    for step in range(1, max_steps + 1):
        response, from_cache = call_model(messages, step, logger)
        if response is None:
            return None

        choice = response.choices[0]
        msg = choice.message

        logger.info(f"\\n--- крок {step} | помилок поспіль={retries} "
                    f"| prompt_tokens={response.usage.prompt_tokens} "
                    f"| completion_tokens={response.usage.completion_tokens}"
                    + (" | з кешу" if from_cache else ""))

        problem = check_response(choice)
        if problem is not None:
            level, text = problem
            logger.info(f"  рівень   : {level}")
            logger.info(f"  текст    : {msg.content}")
            retries = retries + 1
            if retries > config.MAX_RETRIES:
                logger.info("СТОП: модель не змогла сформувати правильний виклик")
                return None
            if text is not None:
                messages.append({"role": "assistant", "content": msg.content})
                messages.append({"role": "user", "content": text})
            continue

        if not msg.tool_calls:
            logger.info(f"ВІДПОВІДЬ: {msg.content}")
            return msg.content

        messages.append(msg)

        model_failed = False
        for call in msg.tool_calls:
            logger.info(f"  виклик   : {call.function.name}({call.function.arguments})")

            level, result = call_tool(call.function.name, call.function.arguments)

            logger.info(f"  рівень   : {level}")
            logger.info(f"  результат: {result}")

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })
            if level in MODEL_ERRORS:
                model_failed = True

        if model_failed:
            retries = retries + 1
            if retries > config.MAX_RETRIES:
                logger.info("СТОП: модель не змогла сформувати правильний виклик")
                return None
        else:
            retries = 0

    logger.info("СТОП: вичерпано ліміт кроків")
    return None
''',

    "tasks.json": '''[
  {
    "id": "Z1",
    "question": "У мене жовтіє листя, що робити?",
    "expected": "назва рослини з корпусу, де згадано цей симптом, і причина"
  },
  {
    "id": "Z2",
    "question": "Як часто підживлювати фікус?",
    "expected": "періодичність у днях із довідника"
  },
  {
    "id": "Z3",
    "question": "Скільки добрива треба фікусу в горщику на 3 літри?",
    "expected": "кількість добрива в мілілітрах"
  },
  {
    "id": "P1",
    "question": "Як доглядати за кактусом сагуаро?",
    "expected": "повідомлення, що такої рослини в корпусі немає"
  },
  {
    "id": "P2",
    "question": "Полий мою рослину",
    "expected": "відмова: агент не виконує фізичних дій"
  }
]
''',

    "agent_runner.py": '''"""Прогін агента на всіх питаннях із tasks.json."""
import json

from langfuse import get_client, propagate_attributes

import config
from agent import run_agent
from utils.lab_logger import custom_logger

logger = custom_logger(config.LAB_LOGFILE_NAME)

with open("tasks.json", encoding="utf-8") as f:
    tasks = json.load(f)

    for task in tasks:
        logger.info(f"\\n### {task['id']} | очікується: {task['expected']}")
        with propagate_attributes(trace_name=f"{config.RUN_TAG}-{task['id']}",
                                  tags=[config.RUN_TAG]):
            run_agent(task["question"])

get_client().flush()
logger.info(f"\\nОброблено задач: {len(tasks)}. Лог: {config.LAB_LOGFILE_NAME}.log")
''',

    "make_task.py": '''"""Створює long_task.json: довге питання, правильну відповідь і мінімум викликів."""
import json
import re

from tools import search_plants, fertilizer_info, calc_dose

ITEMS = [
    ("Фікус Бенджаміна", 2.0),
    ("Фікус Лірата", 3.0),
    ("Заміокулькас", 4.0),
    ("Монстера Деліціоза", 5.0),
    ("Спатифілум", 2.5),
    ("Драцена Маргіната", 3.0),
]

QUESTION = (
    "Для кожної з шести рослин: Фікус Бенджаміна (горщик 2 л), Фікус Лірата (горщик 3 л), "
    "Заміокулькас (горщик 4 л), Монстера Деліціоза (горщик 5 л), Спатифілум (горщик 2.5 л), "
    "Драцена Маргіната (горщик 3 л). Для кожної: (а) знайди в корпусі режим поливу і наведи одним реченням; "
    "(б) знайди в довіднику періодичність підживлення та дозу на літр; "
    "(в) порахуй інструментом загальну дозу добрива для вказаного об'єму горщика. "
    "У кінці назви сумарну дозу добрива для всіх шести рослин у мілілітрах одним числом."
)

MIN_CALLS = 18


def dose_of_one(plant, pot_liters):
    """Обчислює дозу добрива для однієї рослини викликами інструментів."""
    _ = search_plants(plant)
    info = fertilizer_info(plant)
    m = re.search(r"Доза:\\s*([0-9.]+)", info)
    dose_per_liter = float(m.group(1))
    res = calc_dose(pot_liters, dose_per_liter)
    return float(res.replace("мл", "").strip())


def compute():
    """Правильна відповідь: сумарна доза добрива по всіх шести позиціях."""
    total = 0.0
    for plant, pot_liters in ITEMS:
        total = total + dose_of_one(plant, pot_liters)
    return total


def save_task(total):
    task = {
        "id": "L1",
        "question": QUESTION,
        "expected": format(round(total, 2), "g"),
        "min_calls": MIN_CALLS,
    }
    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return task


if __name__ == "__main__":
    task = save_task(compute())
    print("Правильна відповідь:", task["expected"])
    print("Файл long_task.json записано")
''',

    "measure.py": '''"""Запуск довгої задачі в заданій конфігурації."""
import json
import os
import sys
import time

from langfuse import get_client, propagate_attributes

import agent
import config

CONFIGS = {
    "none": {"COMPRESS": "none"},
}


def read_arguments():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    repeats = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    series = sys.argv[3] if len(sys.argv) > 3 else "main"
    names = list(CONFIGS) if which == "all" else [which]
    return names, repeats, series


def load_task():
    with open("long_task.json", encoding="utf-8") as f:
        return json.load(f)


def is_correct(answer, expected):
    if not answer:
        return False
    text = answer.replace(" ", "").replace(",", ".")
    return str(expected) in text


def run_once(name, repeat, series, task):
    for key, value in CONFIGS[name].items():
        setattr(config, key, value)
    run_id = f"{series}_{name}_r{repeat}"

    started = time.time()
    with propagate_attributes(trace_name=f"long-{run_id}", tags=[series, name]):
        answer = agent.run_agent(task=task["question"],
                                 max_steps=config.MAX_STEPS_LONG,
                                 logfile_name=run_id,
                                 log_overwrite=True)
    return run_id, answer, round(time.time() - started, 1)


def main():
    names, repeats, series = read_arguments()
    task = load_task()
    os.makedirs("logs", exist_ok=True)

    for repeat in range(1, repeats + 1):
        for name in names:
            run_id, answer, seconds = run_once(name, repeat, series, task)
            right = is_correct(answer, task["expected"])
            print(f"\\n[{run_id}] час {seconds} с | правильно: {'так' if right else 'ні'}")
            print(f"[{run_id}] відповідь: {(answer or '').replace(chr(10), ' ')[:200]}")

    get_client().flush()


if __name__ == "__main__":
    main()
''',

    "logparse.py": '''"""Читання лога прогону: розбір тексту лога на прогони та кроки."""
import re


def find_status(block):
    if "ПОМИЛКА СЕРВЕРА" in block:
        return "server_error"
    if re.search(r"^ВІДПОВІДЬ:", block, flags=re.M):
        return "final"
    if "СТОП: модель не змогла" in block:
        return "retry_limit"
    if "СТОП: вичерпано ліміт кроків" in block:
        return "step_limit"
    return "unknown"


def parse_step(chunk):
    first_line = chunk.split("\\n", 1)[0]
    prompt = re.search(r"prompt_tokens=(\\d+)", first_line)
    completion = re.search(r"completion_tokens=(\\d+)", first_line)
    squeeze = re.search(r"^  СТИСНЕННЯ: вхід був (\\d+) токенів, повідомлень (\\d+) -> (\\d+)",
                        chunk, flags=re.M)
    extra = re.findall(r"підсумовування коштувало (\\d+) токенів", chunk)
    return {
        "n": int(re.match(r"\\d+", chunk).group()),
        "tokens": int(prompt.group(1)) if prompt else None,
        "completion": int(completion.group(1)) if completion else 0,
        "from_cache": "з кешу" in first_line,
        "calls": re.findall(r"^  виклик   : (.*)$", chunk, flags=re.M),
        "answer": bool(re.search(r"^ВІДПОВІДЬ:", chunk, flags=re.M)),
        "server_error": "ПОМИЛКА СЕРВЕРА" in first_line,
        "squeeze": tuple(int(x) for x in squeeze.groups()) if squeeze else None,
        "extra": sum(int(x) for x in extra),
    }


def parse_run(block):
    chunks = re.split(r"^--- крок ", block, flags=re.M)[1:]
    return {
        "task": block.split("\\n", 1)[0],
        "status": find_status(block),
        "steps": [parse_step(chunk) for chunk in chunks],
    }


def parse_log(text):
    text = re.sub(r"^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2} - [A-Z]+ - ", "", text, flags=re.M)
    blocks = re.split(r"^ЗАДАЧА: ", text, flags=re.M)[1:]
    return [parse_run(block) for block in blocks]
''',

    "metrics.py": '''"""Показники прогону, які рахуються з розібраного лога (див. logparse.py)."""
import statistics

import config


def count_repeats(steps):
    seen = set()
    repeats = 0
    for step in steps:
        for call in step["calls"]:
            if call in seen:
                repeats += 1
            seen.add(call)
    return repeats


def typical_growth(tokens):
    growth = [after - before
              for (_, before), (_, after) in zip(tokens, tokens[1:])
              if after > before]
    return statistics.median(growth) if growth else 0


def find_stall(tokens, typical):
    for (_, before), (number, after) in zip(tokens, tokens[1:]):
        near_window = after >= 0.8 * config.NUM_CTX
        stopped = after - before <= 0.2 * typical
        if near_window and stopped:
            return number
    return None


def describe(run):
    steps = run["steps"]
    tokens = [(s["n"], s["tokens"]) for s in steps if s["tokens"] is not None]
    typical = typical_growth(tokens)
    n = len(tokens)
    first = tokens[0][1] if tokens else 0
    return {
        "status": run["status"],
        "steps": n,
        "repeats": count_repeats(steps),
        "first_tokens": first,
        "typical_growth": typical,
        "max_tokens": max((t for _, t in tokens), default=0),
        "prompt_tokens": sum(t for _, t in tokens),
        "completion_tokens": sum(s["completion"] for s in steps),
        "extra_tokens": sum(s["extra"] for s in steps),
        "formula": n * first + typical * n * (n - 1) / 2,
        "stall": find_stall(tokens, typical),
        "cache_hits": sum(1 for s in steps if s["from_cache"]),
        "squeezes": [s for s in steps if s["squeeze"]],
    }
''',

    "analyze.py": '''r"""Розбір логів прогонів: що відбувалося з входом моделі."""
import os
import sys

import config
from logparse import parse_log
from metrics import describe


def action_lines(step):
    if step["server_error"]:
        return ["ПОМИЛКА СЕРВЕРА"]
    if step["calls"]:
        return [c if len(c) < 60 else c[:57] + "..." for c in step["calls"]]
    if step["answer"]:
        return ["відповідь без виклику"]
    return ["відхилено перевіркою (див. лог)"]


def print_steps(run):
    header = ["Крок", "prompt_tokens", "Приріст", "Що зробила модель"]
    rows = []
    previous = None
    for s in run["steps"]:
        growth = ""
        if previous is not None and s["tokens"] is not None:
            growth = s["tokens"] - previous
        actions = action_lines(s)
        rows.append([str(s["n"]), str(s["tokens"]), str(growth), actions[0]])
        rows += [["", "", "", a] for a in actions[1:]]
        if s["tokens"] is not None:
            previous = s["tokens"]

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

    path_to_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[1])
    with open(path_to_log, encoding="utf-8") as f:
        runs = parse_log(f.read())

    for run in runs:
        print(f"\\nПрогін: {run['task'][:60]}")
        print_summary(run)
        if len(sys.argv) > 2 and sys.argv[2] == "steps":
            print_steps(run)
'''
}

for fname, code in files.items():
    with open(fname, "w", encoding="utf-8") as f:
        f.write(code)

print(">>> 1/3: Створюємо модель qwen25-4k в Ollama...")
subprocess.run(["ollama", "create", "qwen25-4k", "-f", "Modelfile"], check=True)

print(">>> 2/3: Генеруємо long_task.json...")
subprocess.run([sys.executable, "make_task.py"], check=True)

print(">>> 3/3: Запускаємо контрольний прогін 5 коротких задач (logs/run_lab3.log)...")
with open("config.py", "r", encoding="utf-8") as f:
    cfg = f.read()
with open("config.py", "w", encoding="utf-8") as f:
    f.write(cfg.replace('LAB_LOGFILE_NAME = "lab4"', 'LAB_LOGFILE_NAME = "run_lab3"'))

subprocess.run([sys.executable, "agent_runner.py"], check=True)

with open("config.py", "w", encoding="utf-8") as f:
    f.write(cfg)

print("\nЕтап 1 готовий!")
os.remove(__file__)