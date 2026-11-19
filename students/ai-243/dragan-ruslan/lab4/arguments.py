"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchLaptopsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        description="Призначення, характеристика або назва моделі для пошуку в корпусі, "
                    "наприклад 'навчання', 'ігри', 'StudyBook 14'. Не все питання користувача."
    )


class LaptopInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(description="Точна назва моделі ноутбука латиницею, наприклад 'StudyBook 14'")


class CalcInstallmentArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price: float = Field(gt=0, description="Ціна ноутбука в гривнях, отримана з довідника")
    months: int = Field(gt=0, le=36, description="Кількість місяців розстрочки")
    overpay_percent: float = Field(ge=0, description="Відсоток переплати за весь строк")


ARGS = {
    "search_laptops": SearchLaptopsArgs,
    "laptop_info": LaptopInfoArgs,
    "calc_installment": CalcInstallmentArgs,
}
