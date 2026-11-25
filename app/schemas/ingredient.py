from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.validators import not_blank


class IngredientBase(BaseModel):
    name: str = Field(max_length=100, examples=["Брашно"])

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return not_blank(value)


class IngredientCreate(IngredientBase):
    pass


class IngredientUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str:
        return not_blank(value)


class IngredientRead(IngredientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
