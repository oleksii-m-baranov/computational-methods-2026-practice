from pydantic import BaseModel, ConfigDict, Field

class SearchRecipesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(description="Інгредієнт, тип страви або спосіб приготування: одне-два слова українською, не все питання користувача.")

class ProductInfoArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product: str = Field(description="Назва продукту в називному відмінку однини, як у довіднику.")

class ScaleAmountArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    amount: float = Field(gt=0, allow_inf_nan=False, description="Початкова кількість або калорійність на базову вагу.")
    base_servings: float = Field(gt=0, allow_inf_nan=False, description="Базова кількість порцій або базова вага у грамах.")
    target_servings: float = Field(gt=0, allow_inf_nan=False, description="Потрібна кількість порцій або потрібна вага у грамах.")

ARGS = {"search_recipes": SearchRecipesArgs, "product_info": ProductInfoArgs, "scale_amount": ScaleAmountArgs}
