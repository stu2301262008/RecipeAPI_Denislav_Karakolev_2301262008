from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.author_service import AuthorService
from app.services.category_service import CategoryService
from app.services.ingredient_service import IngredientService
from app.services.recipe_service import RecipeService

DbSession = Annotated[Session, Depends(get_db)]


def get_author_service(db: DbSession) -> AuthorService:
    return AuthorService(db)


def get_category_service(db: DbSession) -> CategoryService:
    return CategoryService(db)


def get_ingredient_service(db: DbSession) -> IngredientService:
    return IngredientService(db)


def get_recipe_service(db: DbSession) -> RecipeService:
    return RecipeService(db)


AuthorServiceDep = Annotated[AuthorService, Depends(get_author_service)]
CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
IngredientServiceDep = Annotated[IngredientService, Depends(get_ingredient_service)]
RecipeServiceDep = Annotated[RecipeService, Depends(get_recipe_service)]
