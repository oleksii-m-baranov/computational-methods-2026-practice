"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchLaptopsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Порожній рядок є підрядком будь-якого тексту, тому search_laptops("") повернув би всі ноутбуки каталогу замість відповіді на питання
    query: str = Field(
        min_length=1,
        description="Призначення або характеристика, одне-два слова українською, наприклад 'навчання', 'ігри', 'дизайн'. Не передавай усе питання користувача.")


class LaptopInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Порожня назва не може бути ключем довідника; відсікаємо її схемою, до звернення до даних
    model: str = Field(
        min_length=1,
        description="Точна назва моделі, як вона записана в довіднику, наприклад 'LearnPad 14'.")


class CalcInstallmentArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # Ціна ноутбука не буває нульовою чи від'ємною; у довіднику найдорожча модель коштує 88000 грн, 1000000 грн — стеля із запасом. Межу вибрано самостійно
    price: float = Field(
        gt=0,
        le=1000000,
        description="Ціна ноутбука в гривнях, отримана з довідника через laptop_info.")
    # Нижня межа збігається з перевіркою months <= 0 у calc_installment з lab2 (ділення на кількість місяців). Розстрочка понад 60 місяців (5 років) для ноутбука нереалістична. Верхню межу вибрано самостійно
    months: float = Field(gt=0, le=60, description="Кількість місяців розстрочки.")
    # Переплата 0 допустима (розстрочка без переплати), від'ємної переплати не буває; понад 100% означало б, що платимо більш ніж удвічі. Межу вибрано самостійно
    overpay_percent: float = Field(
        ge=0,
        le=100,
        description="Переплата за весь строк у відсотках, наприклад 10. Якщо переплати немає, передавай 0.")


ARGS = {
    "search_laptops": SearchLaptopsArgs,
    "laptop_info": LaptopInfoArgs,
    "calc_installment": CalcInstallmentArgs,
}
