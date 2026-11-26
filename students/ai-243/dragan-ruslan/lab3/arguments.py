"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field

class SearchLaptopsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        description="Призначення або характеристика, одне-два слова українською, "
                    "наприклад 'навчання', 'ігри', 'програмування'. Не все питання користувача."
    )

class LaptopInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(
        description="Точна назва моделі латиницею, як вона записана в довіднику (наприклад, 'StudyBook 14')."
    )

class CalcInstallmentArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price: float = Field(gt=0, description="Ціна товару в гривнях, отримана з довідника.")
    months: int = Field(gt=0, le=36, description="Кількість місяців розстрочки.")
    overpay_percent: float = Field(
        ge=0,
        description="Переплата за весь строк у відсотках. Якщо переплати немає, передавай 0."
    )

ARGS = {
    "search_laptops": SearchLaptopsArgs,
    "laptop_info": LaptopInfoArgs,
    "calc_installment": CalcInstallmentArgs,
}