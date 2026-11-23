"""Класи аргументів інструментів."""

from pydantic import BaseModel, ConfigDict, Field


class SearchRecipesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(
        min_length=1,
        description=(
            "Інгредієнт, тип страви або спосіб приготування: "
            "одне-два слова українською, наприклад рис, суп або духовка."
        )
    )


class ProductInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: str = Field(
        min_length=1,
        description=(
            "Назва продукту в називному відмінку однини, "
            "у нижньому регістрі, як у довіднику, "
            "наприклад рис або морква."
        )
    )


class ScaleAmountArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(
        gt=0,
        description=(
            "Початкова кількість одного інгредієнта "
            "в оригінальному рецепті."
        )
    )

    base_servings: float = Field(
        gt=0,
        description=(
            "Кількість порцій, на яку розрахований "
            "оригінальний рецепт. Має бути більшою за нуль."
        )
    )

    target_servings: float = Field(
        gt=0,
        description=(
            "Кількість порцій, для якої потрібно "
            "перерахувати інгредієнт."
        )
    )

class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=3, max_length=300,
                       description="Що знайти: одне-два речення українською, словами користувача")


ARGS = {
    "search_recipes": SearchRecipesArgs,
    "product_info": ProductInfoArgs,
    "scale_amount": ScaleAmountArgs,
    "search_docs": DocsArgs
}
