from pydantic import BaseModel, Field, ConfigDict


class SearchLaptopsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=1,
        description="Текстовий запит для пошуку ноутбуків"
    )


class LaptopInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = Field(
        min_length=1,
        description="Точна назва моделі ноутбука"
    )


class CalcInstallmentArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    price: float = Field(
        ge=0,
        description="Вартість ноутбука у гривнях"
    )

    months: float = Field(
        gt=0,
        description="Кількість місяців розстрочки"
    )

    overpay_percent: float = Field(
        description="Відсоток переплати"
    )


ARGUMENT_MODELS = {
    "search_laptops": SearchLaptopsArgs,
    "laptop_info": LaptopInfoArgs,
    "calc_installment": CalcInstallmentArgs
}
