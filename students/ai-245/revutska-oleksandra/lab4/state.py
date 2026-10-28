
"""Збереження стану бібліотечного LLM-агента."""

import json


class AgentState:
    """Зберігає результати викликів інструментів."""

    def __init__(self):
        self.tool_results = []
        self.facts = {}

    def add_tool_result(self, name, arguments, result):
        """Зберігає результат виклику інструмента."""

        if isinstance(arguments, str):
            try:
                parsed_arguments = json.loads(arguments)
            except json.JSONDecodeError:
                parsed_arguments = {"raw": arguments}
        else:
            parsed_arguments = arguments

        record = {
            "tool": name,
            "arguments": parsed_arguments,
            "result": str(result),
        }

        self.tool_results.append(record)

        if name == "book_info":
            title = parsed_arguments.get("title")

            if title:
                self.facts[title] = str(result)

    def get_summary(self):
        """Повертає збережені результати для контексту моделі."""

        if not self.tool_results:
            return "Збережених результатів поки немає."

        lines = ["Збережений стан агента:"]

        for index, record in enumerate(self.tool_results, start=1):
            lines.append(
                f"{index}. {record['tool']} "
                f"{record['arguments']} -> {record['result']}"
            )

        return "\n".join(lines)

    def get_tool_count(self):
        """Повертає кількість виконаних викликів."""

        return len(self.tool_results)

    def clear(self):
        """Очищає стан агента."""

        self.tool_results.clear()
        self.facts.clear()
