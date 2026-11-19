"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchRulesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Порожній рядок є підрядком будь-якого тексту, тому search_rules("") повернув би назви всіх правил корпусу замість відповіді на питання
    query: str = Field(
        min_length=1,
        description="Тип вантажу або обмеження: одне-два слова українською (наприклад, «скло»). Не передавай усе питання користувача цілком.")


class TariffInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Порожня назва не може бути ключем довідника тарифів; відсікаємо її схемою, до звернення до даних
    city: str = Field(
        min_length=1,
        description="Назва міста призначення українською в називному відмінку (наприклад, «Львів», а не «до Львова»)")


class CalcPriceArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Вага посилки не буває нульовою чи від'ємною. Верхня межа 30 кг узята з корпусу (правило «Обмеження за вагою»: максимальна вага однієї посилки — 30 кг)
    weight: float = Field(gt=0, le=30, description="Вага посилки в кілограмах")
    # Ціна за кілограм у довіднику тарифів додатна (13–28 грн/кг); 100 — стеля із запасом, щоб відсікти явно хибні значення. Межу вибрано самостійно
    price_per_kg: float = Field(gt=0, le=100, description="Ціна за кілограм у гривнях, отримана з довідника (tariff_info)")
    # Мінімальна вартість у довіднику — 60–95 грн; нуль чи від'ємне значення не мають змісту, 1000 — стеля із запасом. Межу вибрано самостійно
    min_price: float = Field(
        gt=0,
        le=1000,
        description="Мінімальна вартість відправлення у гривнях, отримана з довідника (tariff_info)")


ARGS = {
    "search_rules": SearchRulesArgs,
    "tariff_info": TariffInfoArgs,
    "calc_price": CalcPriceArgs,
}
