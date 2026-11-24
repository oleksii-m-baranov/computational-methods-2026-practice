
"""Збереження стану задачі агента у JSON."""

import json
import os

import config


class TaskState:
    def __init__(self, task_id):
        self.task_id = task_id
        self.results = []

    def record(self, name, args_raw, result):
        """Зберігає лише унікальні успішні виклики."""

        try:
            args = json.loads(args_raw)
        except (json.JSONDecodeError, TypeError):
            args = {"raw": str(args_raw)}

        # Нормалізуємо аргументи незалежно від порядку полів.
        key = json.dumps(
            args,
            ensure_ascii=False,
            sort_keys=True
        )

        # Перевіряємо, чи такий виклик уже записаний.
        for item in self.results:
            old_key = json.dumps(
                item["args"],
                ensure_ascii=False,
                sort_keys=True
            )

            if item["tool"] == name and old_key == key:
                return

        entry = {
            "tool": name,
            "args": args,
            "result": str(result)
        }

        self.results.append(entry)
        self.save()

    def save(self):
        """Зберігає результати у JSON-файл."""

        os.makedirs("state", exist_ok=True)

        path = os.path.join(
            "state",
            f"{self.task_id}.json"
        )

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                self.results,
                f,
                ensure_ascii=False,
                indent=2
            )

    def render(self):
        """Формує текст стану для контексту моделі."""

        if not self.results:
            return None

        lines = [
            "ЗБЕРЕЖЕНИЙ СТАН ЗАДАЧІ:",
            "Нижче наведено результати вже виконаних інструментів.",
            "Не повторюй успішні виклики без необхідності."
        ]

        for index, item in enumerate(self.results, start=1):
            args = json.dumps(
                item["args"],
                ensure_ascii=False,
                sort_keys=True
            )

            result = item["result"]
            limit = config.STATE_RESULT_CHARS

            if len(result) > limit:
                result = result[:limit] + "..."

            lines.append(
                f"{index}. {item['tool']}({args}) -> {result}"
            )

        return "\n".join(lines)
