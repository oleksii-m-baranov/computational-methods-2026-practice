"""Класи аргументів; описи перенесено з ЛР2."""
from pydantic import BaseModel, ConfigDict, Field

class SearchRecipesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(
        min_length=1,
        description="Слово або короткий запит для пошуку, наприклад курка, рис, суп або духовка.",
    )

class ProductInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product: str = Field(
        min_length=1,
        description="Назва продукту з каталогу, наприклад рис.",
    )

class ScaleAmountArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: float = Field(gt=0, description="Початкова кількість інгредієнта в грамах.")
    base_servings: float = Field(gt=0, description="Кількість порцій у початковому рецепті.")
    target_servings: float = Field(gt=0, description="Бажана кількість порцій.")

ARGS = {
    "search_recipes": SearchRecipesArgs,
    "product_info": ProductInfoArgs,
    "scale_amount": ScaleAmountArgs,
}


class DocsArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=3, max_length=300, description="Що знайти: одне-два речення українською, словами користувача")

ARGS["search_docs"] = DocsArgs
