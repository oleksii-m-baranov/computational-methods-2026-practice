"""Завдання 5, кроки 4-5. Об'єктивні перевірки відповідей із quality.json:
2_format – json.loads(); 4_code – запуск функції top_rated на тестових прикладах."""
import json
import re
import subprocess
import sys

from utils.lab_logger import custom_logger

logger = custom_logger('lab1')


def json_score(text):
    """2 – парситься без правок; 1 – після зрізання обгортки/вступу; 0 – не парситься."""
    try:
        json.loads(text)
        return 2, "парситься без правок"
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", text, re.S)  # зрізаємо ```json ... ``` або «Ось JSON:»
    if match:
        try:
            json.loads(match.group(0))
            return 1, "парситься після видалення обгортки"
        except json.JSONDecodeError:
            pass
    return 0, "не парситься"


def extract_code(text):
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    return "\n".join(blocks) if blocks else text


# модель сама обирає формат films, тому пробуємо три поширені формати
TEST = r'''
SHAPES = {
    "список словників": [{"title": "A", "rating": 7.1}, {"title": "B", "rating": 9.3},
                         {"title": "C", "rating": 8.5}, {"title": "D", "rating": 6.0}],
    "список кортежів": [("A", 7.1), ("B", 9.3), ("C", 8.5), ("D", 6.0)],
    "словник назва->рейтинг": {"A": 7.1, "B": 9.3, "C": 8.5, "D": 6.0},
}
errors = []
for shape, films in SHAPES.items():
    try:
        out = list(top_rated(films, 2))
        s = str(out)
        assert len(out) == 2, f"довжина {len(out)}"
        assert s.find("B") != -1 and s.find("C") != -1 and s.find("B") < s.find("C"), s
        print(f"OK ({shape}):", out)
        break
    except Exception as e:
        errors.append(f"{shape}: {type(e).__name__}: {e}")
else:
    raise SystemExit("жоден формат не пройшов: " + " | ".join(errors))
'''


def run_code(code):
    """Запускає згенерований код з тестом в окремому процесі."""
    proc = subprocess.run([sys.executable, "-I", "-X", "utf8", "-c", code + "\n" + TEST],
                          capture_output=True, text=True, timeout=20, encoding="utf-8")
    if proc.returncode == 0:
        return True, proc.stdout.strip()
    return False, (proc.stderr.strip().splitlines() or ["?"])[-1]


with open("quality.json", encoding="utf-8") as f:
    results = json.load(f)

logger.info("===== ПЕРЕВІРКА quality.json =====")
for model, tasks in results.items():
    for i, answer in enumerate(tasks["2_format"], 1):
        score, verdict = json_score(answer)
        logger.info(f"{model} | 2_format | прогін {i} | json.loads: {verdict} -> {score} б.")
    for i, answer in enumerate(tasks["4_code"], 1):
        ok, info = run_code(extract_code(answer))
        outside = re.sub(r"```(?:python)?\s*\n.*?```", "", answer, flags=re.S).strip()
        has_extra = "```" in answer and bool(outside)
        logger.info(f"{model} | 4_code   | прогін {i} | тест: {'пройдено' if ok else 'ПОМИЛКА'} ({info}); "
                    f"текст поза кодом: {'так' if has_extra else 'ні'}")
