from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.validators import not_blank, optional_text


class CategoryBase(BaseModel):
    name: str = Field(max_length=100, examples=["Десерти"])
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return not_blank(value)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return optional_text(value)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    description: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str:
        return not_blank(value)

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        return optional_text(value)


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
