
"""Стан задачі: результати успішних викликів інструментів."""

import json
import os

import config


def shorten(text, limit):
    """Обрізає довгий текст до limit символів."""
    if len(text) > limit:
        return text[:limit] + "..."
    return text


class TaskState:
    def __init__(self, task_id):
        self.task_id = task_id
        self.results = []

    def record(self, name, args_raw, result):
        """Запам'ятовує результат успішного виклику."""
        self.results.append({
            "tool": name,
            "args": json.loads(args_raw),
            "result": result,
        })
        self.save()

    def save(self):
        """Записує стан у файл."""
        os.makedirs("state", exist_ok=True)
        with open(
            f"state/{self.task_id}.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def format_item(self, item):
        """Форматує один запис для моделі."""
        args = json.dumps(item["args"], ensure_ascii=False)
        result = shorten(item["result"], config.STATE_RESULT_CHARS)
        return f"- {item['tool']}({args}) -> {result}"

    def render(self):
        """Формує текст нагадування для моделі."""
        if not self.results:
            return None

        lines = [
            "РЕЗУЛЬТАТИ ВЖЕ ВИКОНАНИХ ВИКЛИКІВ:",
            "Наведені нижче успішні виклики вже виконані.",
            "НЕ ПОВТОРЮЙ їх із тими самими аргументами.",
            "Використовуй збережені результати для продовження завдання.",
            "Якщо результату для потрібної операції немає, виконай її.",
        ]

        for item in self.results:
            lines.append(self.format_item(item))

        return "\n".join(lines)