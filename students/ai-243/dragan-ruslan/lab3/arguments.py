"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field

class SearchLaptopsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(description="Пошуковий запит (наприклад, 'для навчання' або 'монтаж відео')")

class LaptopInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    model: str = Field(description="Точна назва моделі ноутбука")

class CalcInstallmentArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    price: float = Field(gt=0, description="Ціна ноутбука")
    months: int = Field(gt=0, le=36, description="Кількість місяців розстрочки")
    overpay_percent: float = Field(ge=0, description="Відсоток переплати")

ARGS = {
    "search_laptops": SearchLaptopsArgs,
    "laptop_info": LaptopInfoArgs,
    "calc_installment": CalcInstallmentArgs,
}