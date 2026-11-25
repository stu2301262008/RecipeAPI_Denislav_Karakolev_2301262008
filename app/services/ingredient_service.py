from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.models import Ingredient, RecipeIngredient
from app.schemas.ingredient import IngredientCreate, IngredientUpdate


class IngredientService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Ingredient]:
        stmt = select(Ingredient).order_by(Ingredient.id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def get_by_id(self, ingredient_id: int) -> Ingredient:
        ingredient = self.db.get(Ingredient, ingredient_id)
        if ingredient is None:
            raise NotFoundError(f"Съставка с id={ingredient_id} не е намерена")
        return ingredient

    def create(self, data: IngredientCreate) -> Ingredient:
        self._ensure_name_is_unique(data.name)
        ingredient = Ingredient(**data.model_dump())
        self.db.add(ingredient)
        self.db.commit()
        self.db.refresh(ingredient)
        return ingredient

    def update(self, ingredient_id: int, data: IngredientUpdate) -> Ingredient:
        ingredient = self.get_by_id(ingredient_id)
        values = data.model_dump(exclude_unset=True)
        if "name" in values:
            self._ensure_name_is_unique(values["name"], exclude_id=ingredient_id)
        for field, value in values.items():
            setattr(ingredient, field, value)
        self.db.commit()
        self.db.refresh(ingredient)
        return ingredient

    def delete(self, ingredient_id: int) -> None:
        ingredient = self.get_by_id(ingredient_id)
        is_used = self.db.scalar(select(exists().where(RecipeIngredient.ingredient_id == ingredient_id)))
        if is_used:
            raise ConflictError(f"Съставка с id={ingredient_id} участва в рецепта и не може да бъде изтрита")
        self.db.delete(ingredient)
        self.db.commit()

    def _ensure_name_is_unique(self, name: str, exclude_id: int | None = None) -> None:
        stmt = select(Ingredient.id).where(func.lower(func.trim(Ingredient.name)) == name.strip().lower())
        if exclude_id is not None:
            stmt = stmt.where(Ingredient.id != exclude_id)
        if self.db.scalar(stmt) is not None:
            raise ConflictError(f"Съставка с име '{name}' вече съществува")
