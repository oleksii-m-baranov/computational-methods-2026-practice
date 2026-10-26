"""Класи аргументів інструментів (варіант 2: кулінарія)."""
from pydantic import BaseModel, ConfigDict, Field


class SearchRecipesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    query: str = Field(
        min_length=2,
        max_length=40,
        description="Один інгредієнт, тип страви або спосіб приготування: "
                    "одне-два слова українською в називному відмінку, "
                    "наприклад 'курка', 'суп', 'духовка'. "
                    "Не передавай усе питання користувача цілком.",
    )


class ProductInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    product: str = Field(
        min_length=1,
        max_length=40,
        description="Назва продукту в називному відмінку однини, малими "
                    "літерами, як вона записана в довіднику, наприклад "
                    "'рис' або 'морква'.",
    )


class ScaleAmountArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: float = Field(
        gt=0,
        le=10000,
        description="Кількість інгредієнта в оригінальному рецепті "
                    "(у грамах або мілілітрах)",
    )
    base_servings: int = Field(
        ge=1,
        le=20,
        description="На скільки порцій розрахований рецепт",
    )
    target_servings: int = Field(
        ge=1,
        le=100,
        description="Скільки порцій потрібно",
    )


ARGS = {
    "search_recipes": SearchRecipesArgs,
    "product_info": ProductInfoArgs,
    "scale_amount": ScaleAmountArgs,
}
