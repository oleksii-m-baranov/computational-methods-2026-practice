import json
from providers import make_client

# (варіант 9 - Астрономія).

TEXT = """
Міжнародна космічна станція (МКС) — це пілотована космічна станція на низькій навколоземній орбіті. 
Її будівництво розпочалося у 1998 році з виведення на орбіту першого модуля "Зоря". 
МКС обертається навколо Землі на висоті приблизно 400 кілометрів. 
Станція здійснює один повний оберт навколо планети приблизно за 92 хвилини, що дозволяє космонавтам спостерігати 16 сходів і заходів сонця щодоби. 
Вартість проєкту оцінюється у понад 150 мільярдів доларів, що робить її найдорожчим штучним об'єктом в історії. 
На станції постійно перебуває екіпаж, зазвичай з 7 осіб, які проводять наукові дослідження.
"""

# Завдання для варіанту 9
TASKS = {
    "1_fact": "Рік першого польоту людини в космос. Відповідай лише роком.",
    "2_format": "JSON: event, year, person. Без пояснень, без markdown, лише JSON.",
    "3_summary": "Стисни наступний текст до двох речень, збережи всі числа:\n\n" + TEXT,
    "4_code": "Напиши функцію `light_travel_time(distance_km)`. Лише код.",
    "5_logic": "Зонд рухається зі швидкістю 60000 км/год, відстань 480 млн км. Скільки повних діб триватиме політ? Покажи хід розв'язання.",
    "6_language": "Чим зоря відрізняється від планети. Поясни українською, два абзаци.",
}

results = {}

# Запускаємо для 3-х моделей (дві локальні, одна хмарна)
models_to_test = [
    ("local", "llama3.2:3b"),
    ("local", "qwen3:4b"), 
    ("cloud", "gemini-3.1-flash-lite")
]

for provider, model_name in models_to_test:
    client, model = make_client(provider) # Функція make_client має повертати правильного клієнта для qwen3:4b
    
    # Для qwen3:4b нам треба передати правильне ім'я моделі
    actual_model_name = model_name if provider == "local" else model 
    
    results[actual_model_name] = {}
    print(f"Починаємо тестування моделі: {actual_model_name}")
    
    for task_id, prompt in TASKS.items():
        answers = []
        for attempt in range(2):  # два прогони на завдання
            try:
                r = client.chat.completions.create(
                    model=actual_model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                answers.append(r.choices[0].message.content)
            except Exception as e:
                print(f"Помилка при виконанні {task_id} для {actual_model_name}: {e}")
                answers.append(f"ERROR: {e}")
                
        results[actual_model_name][task_id] = answers
        print(f"  {actual_model_name} / {task_id} — готово")

with open("quality.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Оцінювання завершено. Результати збережено у quality.json")