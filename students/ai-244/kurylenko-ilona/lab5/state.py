"""Стан задачі: збереження результатів викликів інструментів."""

import json
import os

import config


def shorten(text, limit):
    """Скорочує результат, якщо він перевищує ліміт символів."""
    if len(text) > limit:
        return text[:limit] + "..."
    return text


class TaskState:
    """Зберігає успішні результати інструментів поза історією діалогу."""

    def __init__(self, task_id):
        self.task_id = task_id
        self.results = []

    def record(self, name, args_raw, result):
        """Додає результат виклику до стану."""
        self.results.append({
            "tool": name,
            "args": json.loads(args_raw),
            "result": result,
        })
        self.save()

    def save(self):
        """Записує результати до JSON-файлу."""
        os.makedirs("state", exist_ok=True)

        with open(
            f"state/{self.task_id}.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                self.results,
                f,
                ensure_ascii=False,
                indent=2,
            )

    def format_item(self, item):
        """Формує текст одного збереженого результату."""
        args = json.dumps(item["args"], ensure_ascii=False)
        result = shorten(
            item["result"],
            config.STATE_RESULT_CHARS,
        )

        return f"- {item['tool']}({args}) -> {result}"

    def render(self):
        """Створює текстове нагадування з результатами інструментів."""
        if not self.results:
            return None

        lines = [
            "Результати вже виконаних викликів "
            "(збережені програмою):"
        ]

        for item in self.results:
            lines.append(self.format_item(item))

        return "\n".join(lines)