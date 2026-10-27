import json
from providers import ask_model

# Завдання варіанта №9
prompt = """
У якому році відбувся перший політ людини в космос?

Відповідай тільки у форматі JSON:
{
    "event": "назва події",
    "year": 0000,
    "person": "ім'я людини"
}
"""

# Отримуємо відповідь моделі
answer = ask_model(prompt)

print("Відповідь моделі:")
print(answer)

# Перевіряємо правильність
try:
    data = json.loads(answer)

    correct_year = data.get("year") == 1961
    person = str(data.get("person", "")).lower()
    correct_person = (
        "гагарін" in person
        or "gagarin" in person
        or "гагарин" in person
    )
    correct_format = all(
        key in data for key in ["event", "year", "person"]
    )

    result = {
        "model": "llama3.2:3b",
        "task": "Перший політ людини в космос",
        "response": data,
        "correct_year": correct_year,
        "correct_person": correct_person,
        "correct_format": correct_format,
        "passed": correct_year and correct_person and correct_format
    }

except (json.JSONDecodeError, TypeError):
    result = {
        "model": "llama3.2:3b",
        "task": "Перший політ людини в космос",
        "response": answer,
        "passed": False,
        "error": "Неправильний формат JSON"
    }

# Зберігаємо результати
with open("quality.json", "w", encoding="utf-8") as file:
    json.dump(result, file, ensure_ascii=False, indent=4)

print("\nРезультат перевірки:")
print("Успішно:", result["passed"])
print("Результати збережено у quality.json")
