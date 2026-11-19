"""Класи аргументів інструментів. Варіант 9 — Вибір ноутбука."""
from pydantic import BaseModel, ConfigDict, Field


class SearchLaptopsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=2,
        max_length=50,
        description=(
            "Призначення або характеристика, одне-два слова "
            "українською (наприклад 'навчання', 'ігри', "
            "'програмування'). Не передавай все питання "
            "користувача цілком."
        ),
    )


class LaptopInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(
        min_length=2,
        max_length=40,
        description=(
            "Точна назва моделі, як вона записана в довіднику "
            "(наприклад 'StudyBook 14'). Не скорочуй назву."
        ),
    )


class CalcInstallmentArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price: float = Field(
        gt=0,
        le=200000,
        description="Ціна товару в гривнях, отримана з laptop_info.",
    )
    months: int = Field(
        ge=1,
        le=36,
        description="Кількість місяців розстрочки.",
    )
    overpay_percent: float = Field(
        ge=0,
        le=100,
        description=(
            "Переплата за весь строк у відсотках. "
            "Якщо переплати немає — передавай 0."
        ),
    )


ARGS = {
    "search_laptops": SearchLaptopsArgs,
    "laptop_info": LaptopInfoArgs,
    "calc_installment": CalcInstallmentArgs,
}
