import csv
import os


def search_service(query: str) -> str:
    """Пошук підрядком по корпусу. Лаб. 4: повертає ПОВНИЙ текст знайдених файлів
    (раніше — лише першу стрічку), результат не скорочується."""
    q = query.lower()
    found = []
    folder = "data/corpus"
    for filename in sorted(os.listdir(folder)):
        with open(os.path.join(folder, filename), encoding="utf-8") as f:
            text = f.read().strip()
        if q in text.lower():
            found.append(text)
    if not found:
        return f"За запитом '{query}' нічого не знайдено."
    return "\n\n".join(found)


def find_price(service: str):
    """Рядок прайсу для роботи: (work_price, part_price, hours) або None."""
    with open("data/prices.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["service"].lower() == service.lower():
                return float(row["work_price"]), float(row["part_price"]), float(row["hours"])
    return None


def price_info(service: str) -> str:
    with open("data/prices.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["service"].lower() == service.lower():
                return (f"Робота: {row['work_price']} грн, "
                        f"деталь: {row['part_price']} грн за шт., "
                        f"нормо-годин: {row['hours']}")
    return f"Роботи '{service}' немає в прайсі."


def calc_total(work_price: float, part_price: float,
               quantity: float) -> str:
    return f"{round(work_price + part_price * quantity, 2)} грн"


def book_service(service: str) -> str:
    return "Запис на сервіс створено"      # заглушка: агентові ця дія заборонена


TOOLS = {
    "search_service": search_service,
    "price_info": price_info,
    "calc_total": calc_total,
    "book_service": book_service,
}
