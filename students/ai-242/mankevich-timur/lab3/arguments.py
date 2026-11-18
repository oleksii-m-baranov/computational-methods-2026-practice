"""Класи аргументів інструментів."""
from pydantic import BaseModel, ConfigDict, Field


class SearchRecipesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # min_length=1: порожній запит "" збігається з будь-яким рецептом
    query: str = Field(
        min_length=1,
        description="Інгредієнт, тип страви або спосіб приготування: "
                    "одне-два слова українською (наприклад, «курка» або "
                    "«суп»). Не передавай усе питання користувача цілком.")


class ProductInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product: str = Field(
        min_length=1,
        description="Назва продукту в називному відмінку однини, як вона "
                    "записана в довіднику (наприклад, «рис», а не «рису»)")


class ScaleAmountArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # кількість в одиницях рецепта (г, мл): 0 і від'ємні не мають сенсу,
    # 10000 (10 кг) — стеля для домашньої кухні
    amount: float = Field(
        gt=0, le=10000,
        description="Кількість інгредієнта в оригінальному рецепті")
    # корпус: рецепти на 4 порції; 100 порцій — стеля для домашньої кухні
    base_servings: float = Field(
        gt=0, le=100,
        description="На скільки порцій розрахований оригінальний рецепт")
    target_servings: float = Field(
        gt=0, le=100,
        description="Скільки порцій потрібно приготувати")


ARGS = {
    "search_recipes": SearchRecipesArgs,
    "product_info": ProductInfoArgs,
    "scale_amount": ScaleAmountArgs,
}
