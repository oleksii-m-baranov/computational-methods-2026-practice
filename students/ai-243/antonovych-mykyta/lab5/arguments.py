"""Pydantic-класи аргументів інструментів. Варіант 2."""

from pydantic import BaseModel, ConfigDict, Field


class ProductInfoArgs(BaseModel):
    """Аргументи пошуку інформації про продукт."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    product: str = Field(
        min_length=1,
        description=(
            "Назва продукту в називному відмінку однини "
            "у нижньому регістрі, як у довіднику."
        ),
    )


class ScaleAmountArgs(BaseModel):
    """Аргументи перерахунку кількості інгредієнтів."""

    model_config = ConfigDict(extra="forbid")

    amount: float = Field(
        ge=0,
        le=1000000,
        description=(
            "Кількість інгредієнта в оригінальному рецепті."
        ),
    )

    base_servings: float = Field(
        gt=0,
        le=1000,
        description=(
            "Кількість порцій в оригінальному рецепті."
        ),
    )

    target_servings: float = Field(
        gt=0,
        le=1000,
        description=(
            "Кількість порцій, яку потрібно отримати."
        ),
    )


class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    query: str = Field(min_length=2, max_length=500)


ARGS = {
    "search_docs": DocsArgs,
    "product_info": ProductInfoArgs,
    "scale_amount": ScaleAmountArgs,
}
