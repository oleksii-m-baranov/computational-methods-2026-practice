
"""Класи аргументів інструментів."""

from pydantic import BaseModel, ConfigDict, Field


class SearchRecipesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=1,
        max_length=100,
        description=(
            "Інгредієнт, тип страви або спосіб приготування, "
            "одне-два слова українською. Не передавай сюди все "
            "питання користувача цілком."
        ),
    )


class ProductInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: str = Field(
        min_length=1,
        max_length=50,
        description=(
            "Назва продукту в називному відмінку однини, "
            "як вона записана в довіднику. Наприклад: 'рис', "
            "'курка', 'морква'."
        ),
    )


class ScaleAmountArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(
        gt=0,
        le=100000,
        description="Кількість інгредієнта в оригінальному рецепті.",
    )

    base_servings: float = Field(
        gt=0,
        le=1000,
        description="На скільки порцій розрахований рецепт.",
    )

    target_servings: float = Field(
        gt=0,
        le=1000,
        description="Скільки порцій потрібно.",
    )


class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=3,
        max_length=300,
        description="Що знайти: одне-два речення українською, словами користувача",
    )


ARGS = {
    "search_recipes": SearchRecipesArgs,
    "product_info": ProductInfoArgs,
    "scale_amount": ScaleAmountArgs,
    "search_docs": DocsArgs,
}
