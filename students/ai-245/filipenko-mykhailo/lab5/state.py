import json
from pathlib import Path

import config


class TaskState:
    def __init__(self, task_id):
        self.task_id = str(task_id)
        self.records = []

        self.path = Path("state") / f"{self.task_id}.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, name, args_raw, result):
        item = {
            "tool": str(name),
            "arguments": str(args_raw),
            "result": str(result)
        }

        self.records.append(item)
        self.save()

    def save(self):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                self.records,
                file,
                ensure_ascii=False,
                indent=2
            )

    def render(self):
        lines = []

        for item in self.records:
            result = item["result"]

            if len(result) > config.STATE_RESULT_CHARS:
                result = result[:config.STATE_RESULT_CHARS] + "..."

            lines.append(
                f"- {item['tool']}({item['arguments']}) -> {result}"
            )

        return "\n".join(lines)
