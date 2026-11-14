"""Класи аргументів інструментів."""

from pydantic import BaseModel, ConfigDict, Field


class SearchLaptopsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=1,
        description="Призначення або характеристика ноутбука, "
                    "одне-два слова українською, не все питання користувача."
    )


class LaptopInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(
        min_length=1,
        description="Точна назва моделі ноутбука, як вона записана в довіднику."
    )


class CalcInstallmentArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    price: float = Field(
        gt=0,
        description="Ціна ноутбука в гривнях, отримана з довідника."
    )

    months: float = Field(
        gt=0,
        description="Кількість місяців розстрочки."
    )

    overpay_percent: float = Field(
        ge=0,
        description="Переплата за весь строк у відсотках. "
                    "Якщо переплати немає, передавай 0."
    )


ARGS = {
    "search_laptops": SearchLaptopsArgs,
    "laptop_info": LaptopInfoArgs,
    "calc_installment": CalcInstallmentArgs,
}