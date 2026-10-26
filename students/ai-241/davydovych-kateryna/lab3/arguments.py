"""Класи аргументів інструментів (варіант 9 – вибір ноутбука).

З цих класів генерується опис параметрів для моделі (schemas.py),
і ними ж диспетчер перевіряє відповідь моделі (dispatcher.py).
"""
from pydantic import BaseModel, ConfigDict, Field


class SearchLaptopsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=2,
        max_length=30,
        description="Призначення або характеристика, одне-два слова "
                    "українською, наприклад 'навчання', 'ігри', 'дизайн'. "
                    "Не передавай усе питання користувача.",
    )


class LaptopInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(
        min_length=2,
        max_length=40,
        description="Точна назва моделі, як вона записана в довіднику, "
                    "наприклад 'StudyBook 14'.",
    )


class CalcInstallmentArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price: float = Field(
        gt=0,
        le=100000,
        description="Ціна ноутбука в гривнях, отримана з довідника "
                    "через laptop_info.",
    )
    months: int = Field(
        ge=1,
        le=24,
        description="Кількість місяців розстрочки.",
    )
    overpay_percent: float = Field(
        ge=0,
        le=100,
        description="Переплата за весь строк у відсотках, наприклад 10. "
                    "Якщо переплати немає, передавай 0.",
    )


ARGS = {
    "search_laptops": SearchLaptopsArgs,
    "laptop_info": LaptopInfoArgs,
    "calc_installment": CalcInstallmentArgs,
}
