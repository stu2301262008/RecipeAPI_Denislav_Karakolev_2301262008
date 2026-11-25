from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.models import Category, Recipe
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Category]:
        stmt = select(Category).order_by(Category.id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def get_by_id(self, category_id: int) -> Category:
        category = self.db.get(Category, category_id)
        if category is None:
            raise NotFoundError(f"Категория с id={category_id} не е намерена")
        return category

    def create(self, data: CategoryCreate) -> Category:
        self._ensure_name_is_unique(data.name)
        category = Category(**data.model_dump())
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, category_id: int, data: CategoryUpdate) -> Category:
        category = self.get_by_id(category_id)
        values = data.model_dump(exclude_unset=True)
        if "name" in values:
            self._ensure_name_is_unique(values["name"], exclude_id=category_id)
        for field, value in values.items():
            setattr(category, field, value)
        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, category_id: int) -> None:
        category = self.get_by_id(category_id)
        self.db.delete(category)
        self.db.commit()

    def get_recipes(self, category_id: int) -> list[Recipe]:
        self.get_by_id(category_id)
        stmt = select(Recipe).where(Recipe.category_id == category_id).order_by(Recipe.id)
        return list(self.db.scalars(stmt))

    def _ensure_name_is_unique(self, name: str, exclude_id: int | None = None) -> None:
        stmt = select(Category.id).where(func.lower(func.trim(Category.name)) == name.strip().lower())
        if exclude_id is not None:
            stmt = stmt.where(Category.id != exclude_id)
        if self.db.scalar(stmt) is not None:
            raise ConflictError(f"Категория с име '{name}' вече съществува")
