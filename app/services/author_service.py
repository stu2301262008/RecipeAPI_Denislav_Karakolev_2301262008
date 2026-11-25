from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.models import Author, Recipe
from app.schemas.author import AuthorCreate, AuthorUpdate


class AuthorService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Author]:
        stmt = select(Author).order_by(Author.id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def get_by_id(self, author_id: int) -> Author:
        author = self.db.get(Author, author_id)
        if author is None:
            raise NotFoundError(f"Автор с id={author_id} не е намерен")
        return author

    def create(self, data: AuthorCreate) -> Author:
        self._ensure_email_is_unique(data.email)
        author = Author(**data.model_dump())
        self.db.add(author)
        self.db.commit()
        self.db.refresh(author)
        return author

    def update(self, author_id: int, data: AuthorUpdate) -> Author:
        author = self.get_by_id(author_id)
        values = data.model_dump(exclude_unset=True)
        if "email" in values:
            self._ensure_email_is_unique(values["email"], exclude_id=author_id)
        for field, value in values.items():
            setattr(author, field, value)
        self.db.commit()
        self.db.refresh(author)
        return author

    def delete(self, author_id: int) -> None:
        author = self.get_by_id(author_id)
        has_recipes = self.db.scalar(select(exists().where(Recipe.author_id == author_id)))
        if has_recipes:
            raise ConflictError(f"Автор с id={author_id} има рецепти и не може да бъде изтрит")
        self.db.delete(author)
        self.db.commit()

    def get_recipes(self, author_id: int) -> list[Recipe]:
        self.get_by_id(author_id)
        stmt = select(Recipe).where(Recipe.author_id == author_id).order_by(Recipe.id)
        return list(self.db.scalars(stmt))

    def _ensure_email_is_unique(self, email: str, exclude_id: int | None = None) -> None:
        stmt = select(Author.id).where(func.lower(Author.email) == email.strip().lower())
        if exclude_id is not None:
            stmt = stmt.where(Author.id != exclude_id)
        if self.db.scalar(stmt) is not None:
            raise ConflictError(f"Автор с имейл '{email}' вече съществува")
