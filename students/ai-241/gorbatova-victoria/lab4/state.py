"""Стан задачі: результати успішних викликів інструментів, які зберігає програма."""
import json
import os
import config


def shorten(text, limit):
    """Обрізає довгий текст до limit символів і додає «...»."""
    if len(text) > limit:
        return text[:limit] + "..."
    return text


class TaskState:
    def __init__(self, task_id):
        self.task_id = task_id             # ім'я файла: state/<task_id>.json
        self.results = []                  # список записів

    def record(self, name, args_raw, result):
        """Запам'ятовує результат одного успішного виклику інструмента."""
        self.results.append({
            "tool": name,
            "args": json.loads(args_raw),
            "result": result,
        })
        self.save()

    def save(self):
        """Записує весь стан у файл."""
        os.makedirs("state", exist_ok=True)
        with open(f"state/{self.task_id}.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def format_item(self, item):
        """Один запис у вигляді рядка."""
        args = json.dumps(item["args"], ensure_ascii=False)
        result = shorten(item["result"], config.STATE_RESULT_CHARS)
        return f"- {item['tool']}({args}) -> {result}"

    def render(self):
        """Текст для моделі: заголовок і по рядку на кожен збережений результат."""
        if not self.results:
            return None
        lines = ["Результати вже виконаних викликів (збережені програмою):"]
        for item in self.results:
            lines.append(self.format_item(item))
        return "\n".join(lines)