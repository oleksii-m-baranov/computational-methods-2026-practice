import json
from pathlib import Path

task_file = Path("long_task.json")
generator = Path("make_task.py")
backup = Path("before_ordered_task")
backup.mkdir(exist_ok=True)

if (backup / "long_task.json").exists():
    raise SystemExit("STOP: backup already exists. Send this message.")

task = json.loads(task_file.read_text(encoding="utf-8"))
source = generator.read_text(encoding="utf-8-sig")

instruction = """
Працюй послідовно, по одному продукту, у порядку зі списку.
Для поточного продукту спочатку виклич search_recipes,
потім product_info для цього самого продукту.
Дочекайся результату довідника. Після цього виклич scale_amount:
amount — отримана калорійність на 100 г,
base_servings — 100, target_servings — задана вага в грамах.
Після отримання результату переходь до наступного продукту.
За одну відповідь викликай лише один інструмент.
Не підставляй кількість порцій рецепта замість ваги продукту.
Не завершуй відповідь, поки не опрацюєш усі шість продуктів.
Якщо даних немає, прямо зазнач це, не вигадуй числа.
Фінальну відповідь подай українською.
"""

question = task["question"] + "\n\n" + instruction.strip()
start = source.index("QUESTION =")
end = source.index("MIN_CALLS =", start)

(backup / "long_task.json").write_bytes(task_file.read_bytes())
(backup / "make_task.py").write_bytes(generator.read_bytes())

task["question"] = question
generator.write_text(
    source[:start] + "QUESTION = " + repr(question) + "\n" + source[end:],
    encoding="utf-8",
)
task_file.write_text(
    json.dumps(task, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print("TASK UPDATED. Original files saved in before_ordered_task.")