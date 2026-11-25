from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.exceptions import ConflictError, NotFoundError
from app.models import Author, Category, Ingredient, Recipe, RecipeIngredient
from app.schemas.ingredient import IngredientRead
from app.schemas.recipe import RecipeCreate, RecipeRead, RecipeScaledRead, RecipeUpdate
from app.schemas.recipe_ingredient import (
    RecipeIngredientCreate,
    RecipeIngredientRead,
    RecipeIngredientUpdate,
)


class RecipeService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(
        self,
        title: str | None = None,
        category_id: int | None = None,
        max_prep_time: int | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Recipe]:
        stmt = select(Recipe)
        if title is not None and title.strip():
            stmt = stmt.where(func.lower(Recipe.title).contains(title.strip().lower(), autoescape=True))
        if category_id is not None:
            stmt = stmt.where(Recipe.category_id == category_id)
        if max_prep_time is not None:
            stmt = stmt.where(Recipe.prep_time_minutes <= max_prep_time)
        stmt = stmt.order_by(Recipe.id).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def get_by_id(self, recipe_id: int) -> Recipe:
        recipe = self.db.get(Recipe, recipe_id)
        if recipe is None:
            raise NotFoundError(f"Рецепта с id={recipe_id} не е намерена")
        return recipe

    def create(self, data: RecipeCreate) -> Recipe:
        self._ensure_author_exists(data.author_id)
        if data.category_id is not None:
            self._ensure_category_exists(data.category_id)
        self._ensure_title_is_unique(data.author_id, data.title)

        recipe = Recipe(**data.model_dump())
        self.db.add(recipe)
        self.db.commit()
        self.db.refresh(recipe)
        return recipe

    def update(self, recipe_id: int, data: RecipeUpdate) -> Recipe:
        recipe = self.get_by_id(recipe_id)
        values = data.model_dump(exclude_unset=True)

        if "author_id" in values:
            self._ensure_author_exists(values["author_id"])
        if values.get("category_id") is not None:
            self._ensure_category_exists(values["category_id"])
        if "title" in values or "author_id" in values:
            self._ensure_title_is_unique(
                values.get("author_id", recipe.author_id),
                values.get("title", recipe.title),
                exclude_id=recipe_id,
            )

        for field, value in values.items():
            setattr(recipe, field, value)
        self.db.commit()
        self.db.refresh(recipe)
        return recipe

    def delete(self, recipe_id: int) -> None:
        recipe = self.get_by_id(recipe_id)
        self.db.delete(recipe)
        self.db.commit()

    def get_ingredients(self, recipe_id: int) -> list[RecipeIngredient]:
        self.get_by_id(recipe_id)
        stmt = (
            select(RecipeIngredient)
            .options(joinedload(RecipeIngredient.ingredient))
            .where(RecipeIngredient.recipe_id == recipe_id)
            .order_by(RecipeIngredient.id)
        )
        return list(self.db.scalars(stmt))

    def add_ingredient(self, recipe_id: int, data: RecipeIngredientCreate) -> RecipeIngredient:
        recipe = self.get_by_id(recipe_id)
        ingredient = self.db.get(Ingredient, data.ingredient_id)
        if ingredient is None:
            raise NotFoundError(f"Съставка с id={data.ingredient_id} не е намерена")
        if self._find_link(recipe_id, data.ingredient_id) is not None:
            raise ConflictError(f"Съставка с id={data.ingredient_id} вече е добавена към рецепта с id={recipe_id}")

        link = RecipeIngredient(recipe=recipe, ingredient=ingredient, quantity=data.quantity, unit=data.unit)
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link

    def update_ingredient(
        self, recipe_id: int, ingredient_id: int, data: RecipeIngredientUpdate
    ) -> RecipeIngredient:
        link = self._get_link(recipe_id, ingredient_id)
        for field, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
            setattr(link, field, value)
        self.db.commit()
        self.db.refresh(link)
        return link

    def remove_ingredient(self, recipe_id: int, ingredient_id: int) -> None:
        link = self._get_link(recipe_id, ingredient_id)
        self.db.delete(link)
        self.db.commit()

    def get_scaled(self, recipe_id: int, servings: int) -> RecipeScaledRead:
        recipe = self.get_by_id(recipe_id)
        factor = servings / recipe.servings
        ingredients = [
            RecipeIngredientRead(
                ingredient=IngredientRead.model_validate(link.ingredient),
                quantity=round(link.quantity * factor, 2),
                unit=link.unit,
            )
            for link in self.get_ingredients(recipe_id)
        ]
        recipe_data = RecipeRead.model_validate(recipe).model_dump()
        recipe_data["servings"] = servings
        return RecipeScaledRead(**recipe_data, original_servings=recipe.servings, ingredients=ingredients)

    def _find_link(self, recipe_id: int, ingredient_id: int) -> RecipeIngredient | None:
        stmt = (
            select(RecipeIngredient)
            .options(joinedload(RecipeIngredient.ingredient))
            .where(RecipeIngredient.recipe_id == recipe_id, RecipeIngredient.ingredient_id == ingredient_id)
        )
        return self.db.scalar(stmt)

    def _get_link(self, recipe_id: int, ingredient_id: int) -> RecipeIngredient:
        self.get_by_id(recipe_id)
        link = self._find_link(recipe_id, ingredient_id)
        if link is None:
            raise NotFoundError(f"Съставка с id={ingredient_id} не е част от рецепта с id={recipe_id}")
        return link

    def _ensure_author_exists(self, author_id: int) -> None:
        if self.db.get(Author, author_id) is None:
            raise NotFoundError(f"Автор с id={author_id} не е намерен")

    def _ensure_category_exists(self, category_id: int) -> None:
        if self.db.get(Category, category_id) is None:
            raise NotFoundError(f"Категория с id={category_id} не е намерена")

    def _ensure_title_is_unique(self, author_id: int, title: str, exclude_id: int | None = None) -> None:
        stmt = select(Recipe.id).where(
            Recipe.author_id == author_id,
            func.lower(func.trim(Recipe.title)) == title.strip().lower(),
        )
        if exclude_id is not None:
            stmt = stmt.where(Recipe.id != exclude_id)
        if self.db.scalar(stmt) is not None:
            raise ConflictError(f"Авторът вече има рецепта със заглавие '{title}'")
