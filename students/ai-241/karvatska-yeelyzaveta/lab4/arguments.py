from pydantic import BaseModel, ConfigDict, Field, field_validator


class SearchRecipesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    query: str = Field(min_length=1, max_length=120)


class ProductInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    product: str = Field(min_length=1, max_length=80)


class ScaleAmountArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(gt=0, le=100000)
    base_servings: float = Field(gt=0, le=1000)
    target_servings: float = Field(gt=0, le=1000)


ARGS = {
    "search_recipes": SearchRecipesArgs,
    "product_info": ProductInfoArgs,
    "scale_amount": ScaleAmountArgs,
}
