from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class SearchRecipesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(description="Інгредієнт або тип страви українською.")


class ProductInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product: str = Field(description="Назва продукту в називному відмінку.")


class ScaleAmountArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: float = Field(gt=0, description="Кількість інгредієнта.")
    base_servings: float = Field(gt=0, description="Базова кількість порцій.")
    target_servings: float = Field(gt=0, description="Цільова кількість порцій.")


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