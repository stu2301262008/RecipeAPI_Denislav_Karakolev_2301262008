from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import Unit
from app.schemas.ingredient import IngredientRead


class RecipeIngredientCreate(BaseModel):
    ingredient_id: int = Field(gt=0)
    quantity: float = Field(gt=0, examples=[200])
    unit: Unit


class RecipeIngredientUpdate(BaseModel):
    quantity: float | None = Field(default=None, gt=0)
    unit: Unit | None = None

    @model_validator(mode="after")
    def check_not_empty(self) -> "RecipeIngredientUpdate":
        if self.quantity is None and self.unit is None:
            raise ValueError("Трябва да се подаде поне едно от полетата quantity или unit")
        return self


class RecipeIngredientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ingredient: IngredientRead
    quantity: float
    unit: Unit
