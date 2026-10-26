"""Крок 4 завдання 5: об'єктивна перевірка завдання 2 через json.loads()."""
import json
import re
from utils.lab_logger import custom_logger

logger = custom_logger("lab1")

with open("quality.json", encoding="utf-8") as f:
    data = json.load(f)

for model, tasks in data.items():
    for i, answer in enumerate(tasks["2_format"], 1):
        try:
            json.loads(answer)
            verdict = "2 бали: парситься без правок"
        except json.JSONDecodeError:
            stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", answer.strip())
            try:
                json.loads(stripped)
                verdict = "1 бал: парситься після зрізання markdown-обгортки"
            except json.JSONDecodeError:
                verdict = "0 балів: не парситься"
        logger.info(f"{model} / прогін {i}: {verdict}")
