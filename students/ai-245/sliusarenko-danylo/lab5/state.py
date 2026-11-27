"""Стан задачі: результати успішних викликів інструментів."""
import json
import os
import config


def shorten(text, limit):
    if len(text) > limit:
        return text[:limit] + "..."
    return text


class TaskState:
    def __init__(self, task_id):
        self.task_id = task_id
        self.results = []

    def record(self, name, args_raw, result):
        self.results.append({
            "tool": name,
            "args": json.loads(args_raw),
            "result": result,
        })
        self.save()

    def save(self):
        os.makedirs("state", exist_ok=True)
        with open(f"state/{self.task_id}.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

    def format_item(self, item):
        args = json.dumps(item["args"], ensure_ascii=False)
        result = shorten(item["result"], config.STATE_RESULT_CHARS)
        return f"- {item['tool']}({args}) -> {result}"

    def render(self):
        if not self.results:
            return None
        lines = ["Результати вже виконаних викликів (збережені програмою):"]
        for item in self.results:
            lines.append(self.format_item(item))
        return "\n".join(lines)