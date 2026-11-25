"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchServiceArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Порожній рядок є підрядком будь-якого тексту, тому search_service("") повернув би всі роботи корпусу замість відповіді на питання
    query: str = Field(
        min_length=1,
        description="Вузол автомобіля або пробіг, одне-два слова українською, наприклад 'гальма', 'двигун', '60 тисяч'. Не передавай усе питання користувача.")


class PriceInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Порожня назва не може бути ключем прайсу; відсікаємо її схемою, до звернення до даних
    service: str = Field(
        min_length=1,
        description="Назва роботи в нижньому регістрі, як вона записана в прайсі, наприклад 'заміна масла'.")


class CalcTotalArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Вартість роботи не буває від'ємною. У прайсі робота коштує від 300 до 3000 грн, 100000 грн — стеля з великим запасом. Межу вибрано самостійно
    work_price: float = Field(
        ge=0,
        le=100000,
        description="Вартість роботи в гривнях, отримана з прайсу через price_info.")
    # Нуль дозволений: у прайсі чистка дросельної заслінки має part_price = 0 (деталі немає). Від'ємна ціна безглузда; у прайсі максимум 4800 грн. Межу вибрано самостійно
    part_price: float = Field(
        ge=0,
        le=100000,
        description="Вартість однієї деталі в гривнях, отримана з прайсу через price_info.")
    # Кількість деталей — додатне число: у lab2 в описі сказано «якщо не назвав, передавай 1». Максимум у запитах — 4 літри масла; 100 — стеля з запасом. Межу вибрано самостійно
    quantity: float = Field(gt=0, le=100, description="Кількість деталей. Якщо користувач не назвав, передавай 1.")


ARGS = {
    "search_service": SearchServiceArgs,
    "price_info": PriceInfoArgs,
    "calc_total": CalcTotalArgs,
}
