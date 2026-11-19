"""Чому базовий прогін відрізняється від lab2.log на Z3 (відповідь на зауваження до PR).

Перший крок агента лабораторної № 2 на задачі Z3 повторюється N разів з тими самими
повідомленнями, описами інструментів і моделлю, що в lab2/config.py та lab2/schemas.py:
  1) TEMPERATURE = 0.2 без seed — як у lab2 і в базовому прогоні;
  2) TEMPERATURE = 0.2 і seed = 42;
  3) TEMPERATURE = 0.
Якщо вхід той самий (однаковий prompt_tokens), а рішення різні лише в режимі 1,
розбіжність дає випадковий вибір токенів, а не зміна коду чи моделі."""
import importlib.util
import json
from collections import Counter
from pathlib import Path

from openai import OpenAI

from utils.lab_logger import custom_logger

N = 20
LAB2 = Path(__file__).resolve().parent.parent / "lab2"


def load_lab2(name):
    """Модуль саме з lab2/, щоб не сплутати з однойменними файлами lab3."""
    spec = importlib.util.spec_from_file_location(f"lab2_{name}", LAB2 / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


config = load_lab2("config")
SCHEMAS = load_lab2("schemas").SCHEMAS
tasks = json.loads((LAB2 / "tasks.json").read_text(encoding="utf-8"))
z3 = next(t for t in tasks if t["id"] == "Z3")

client = OpenAI(base_url=config.BASE_URL, api_key=config.API_KEY)
logger = custom_logger("lab3_seed_check")

messages = [
    {"role": "system", "content": config.SYSTEM},
    {"role": "user", "content": z3["question"]},
]

MODES = [
    ("temperature=0.2, без seed (як у lab2)", {"temperature": config.TEMPERATURE}),
    ("temperature=0.2, seed=42", {"temperature": config.TEMPERATURE, "seed": 42}),
    ("temperature=0", {"temperature": 0}),
]

logger.info(f"Модель: {config.MODEL} | задача Z3: {z3['question']}")
logger.info(f"Перший крок агента lab2, по {N} запитів на режим")

for title, params in MODES:
    logger.info(f"\n=== {title}")
    decisions = Counter()
    prompt_tokens = set()
    for i in range(1, N + 1):
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=messages,
            tools=SCHEMAS,
            **params,
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            decision = " + ".join(f"{c.function.name}({c.function.arguments})" for c in msg.tool_calls)
        else:
            decision = f"відповідь без виклику: {msg.content}"
        decisions[decision] += 1
        prompt_tokens.add(response.usage.prompt_tokens)
        logger.info(f"{i:2d}. prompt_tokens={response.usage.prompt_tokens} | {decision}")

    logger.info(f"--- підсумок ({title}): prompt_tokens={sorted(prompt_tokens)}, "
                f"різних рішень: {len(decisions)}")
    for decision, count in decisions.most_common():
        logger.info(f"  {count:2d} з {N}: {decision}")
