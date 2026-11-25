from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.validators import not_blank, optional_text


class AuthorBase(BaseModel):
    name: str = Field(max_length=100, examples=["Иван Иванов"])
    email: EmailStr = Field(examples=["ivan@example.com"])
    bio: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return not_blank(value)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, value: str | None) -> str | None:
        return optional_text(value)


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    email: EmailStr | None = None
    bio: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str:
        return not_blank(value)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("Полето не може да бъде null")
        return value.strip().lower()

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, value: str | None) -> str | None:
        return optional_text(value)


class AuthorRead(AuthorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
