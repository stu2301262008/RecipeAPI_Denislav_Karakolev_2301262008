from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import Difficulty
from app.schemas.recipe_ingredient import RecipeIngredientRead
from app.schemas.validators import not_blank


class RecipeBase(BaseModel):
    title: str = Field(max_length=200, examples=["Палачинки"])
    instructions: str = Field(examples=["Смесете съставките и изпечете."])
    prep_time_minutes: int = Field(gt=0, examples=[30])
    servings: int = Field(gt=0, examples=[4])
    difficulty: Difficulty
    category_id: int | None = None

    @field_validator("title", "instructions")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return not_blank(value)


class RecipeCreate(RecipeBase):
    author_id: int


class RecipeUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    instructions: str | None = None
    prep_time_minutes: int | None = Field(default=None, gt=0)
    servings: int | None = Field(default=None, gt=0)
    difficulty: Difficulty | None = None
    author_id: int | None = None
    category_id: int | None = None

    @field_validator("title", "instructions")
    @classmethod
    def validate_text(cls, value: str | None) -> str:
        return not_blank(value)

    @field_validator("prep_time_minutes", "servings", "difficulty", "author_id")
    @classmethod
    def not_null(cls, value):
        if value is None:
            raise ValueError("Полето не може да бъде null")
        return value


class RecipeRead(RecipeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int


class RecipeScaledRead(RecipeRead):
    original_servings: int
    ingredients: list[RecipeIngredientRead]
