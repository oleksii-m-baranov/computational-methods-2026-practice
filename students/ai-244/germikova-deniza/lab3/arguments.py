
from pydantic import BaseModel, ConfigDict, Field


class SearchRecipesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)


class ProductInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: str = Field(min_length=1)


class ScaleAmountArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(gt=0)
    base_servings: float = Field(gt=0)
    target_servings: float = Field(gt=0)


ARGS = {
    "search_recipes": SearchRecipesArgs,
    "product_info": ProductInfoArgs,
    "scale_amount": ScaleAmountArgs,
}

