import json
from tools import search_books, book_info, calculate

# 6 книг із каталогу студента:
SELECTED_BOOKS = [
    ("Основи алгоритмів", 2),
    ("Місто вічної ночі", 3),
    ("Кулінарія для лінивих", 4),
    ("Тіні старого Києва", 2),
    ("Місто вічної зорі", 1),
    ("Основи баз даних", 2),
]

def generate_long_task():
    subtasks = []
    total_fine = 0

    for title, copies in SELECTED_BOOKS:
        # 1. Пошук анотації
        res_search = search_books(title)
        
        # 2. Отримання умов видачі
        res_info = book_info(title)
        # Парсимо штраф
        fine = 0
        for part in res_info.split(","):
            if "штраф" in part:
                fine = int(part.split(":")[1].replace("грн/день", "").strip())
        
        # 3. Розрахунок затримки на 3 дні
        sub_fine = int(float(calculate("mul", fine * copies, 3)))
        total_fine += sub_fine
        
        subtasks.append(f"{title} ({copies} книж{'ки' if copies < 5 else 'ок'})")

    question = (
        f"Для кожної з шести книжок: {', '.join(subtasks)}. "
        "Для кожної: (а) термін видачі в днях, і наведи одним реченням; "
        "(б) знайди в довіднику штраф за затримку повернення книжки; "
        "(в) порахуй вартість затримки на 3 дні для заданої кількості книжок. "
        "У кінці назви загальну суму штрафу для усіх книжок."
    )

    task = {
        "id": "L1",
        "question": question,
        "expected": str(total_fine),
        "min_calls": len(SELECTED_BOOKS) * 3,
    }

    with open("long_task.json", "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)

    print(f"Згенеровано long_task.json: очікувана сума = {total_fine} грн, min_calls = {task['min_calls']}")

if __name__ == "__main__":
    generate_long_task()
