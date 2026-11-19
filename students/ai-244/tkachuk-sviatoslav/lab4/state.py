"""Збереження успішних результатів інструментів поза контекстом."""
import json
from pathlib import Path
import config

ROOT = Path(__file__).resolve().parent


class TaskState:
    def __init__(self, task_id):
        self.task_id = task_id
        self.results = []

    def record(self, name, args_raw, result):
        self.results.append({"tool": name, "args": json.loads(args_raw), "result": result})
        self.save()

    def save(self):
        folder = ROOT / "state"
        folder.mkdir(exist_ok=True)
        (folder / f"{self.task_id}.json").write_text(
            json.dumps(self.results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def render(self):
        if not self.results:
            return None
        lines = ["Результати вже виконаних викликів (збережені програмою):"]
        for item in self.results:
            args = json.dumps(item["args"], ensure_ascii=False, sort_keys=True)
            result = item["result"][:config.STATE_RESULT_CHARS]
            if len(item["result"]) > config.STATE_RESULT_CHARS:
                result += "..."
            lines.append(f"- {item['tool']}({args}) -> {result}")
        return "\n".join(lines)
