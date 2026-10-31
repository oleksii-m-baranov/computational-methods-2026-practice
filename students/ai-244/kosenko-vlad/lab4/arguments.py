"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=1,
        max_length=40,
        description=("Призначення або ключова характеристика ноутбука (одне-два слова українською, "
                     "наприклад: 'ігри', 'навчання', 'офісна робота', 'легкий') "
                     "або точна назва моделі. "
                     "Не передавати все запитання користувача."),
    )


class InfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(
        min_length=1,
        max_length=60,
        description="Точна назва моделі ноутбука так, як вона записана в довіднику.",
    )


class InstallmentArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price: float = Field(
        gt=0,
        le=200000,
        description="Ціна товару в гривнях, отримана з довідника товарів.",
    )
    months: int = Field(
        ge=1,
        le=36,
        description="Кількість місяців розстрочки (ціле число від 1 до 36).",
    )
    overpay_percent: float = Field(
        ge=0,
        le=100,
        description=("Загальна переплата за весь строк у відсотках (наприклад, 0 якщо без переплат, "
                     "або 5 для 5%). Якщо переплати немає — передавати 0."),
    )


ARGS = {
    "search_laptops": SearchArgs,
    "laptop_info": InfoArgs,
    "calc_installment": InstallmentArgs,
}
