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
        gt=0,
        description="Вартість ноутбука у гривнях"
    )

    months: int = Field(
        ge=1,
        le=60,
        description="Кількість місяців розстрочки"
    )

    overpay_percent: float = Field(
        ge=0,
        le=100,
        description="Відсоток переплати"
    )


class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=3,
        max_length=300,
        description="Що знайти: одне-два речення українською, словами користувача"
    )


ARGUMENT_MODELS = {
    "search_laptops": SearchLaptopsArgs,
    "laptop_info": LaptopInfoArgs,
    "calc_installment": CalcInstallmentArgs,
    "search_docs": DocsArgs
}
