from typing import Annotated

from fastapi import APIRouter, Query, status

from app.config import MAX_SERVINGS
from app.dependencies import RecipeServiceDep
from app.schemas.recipe import RecipeCreate, RecipeRead, RecipeScaledRead, RecipeUpdate
from app.schemas.recipe_ingredient import (
    RecipeIngredientCreate,
    RecipeIngredientRead,
    RecipeIngredientUpdate,
)

router = APIRouter(prefix="/recipes", tags=["Recipes"])


@router.get("/", response_model=list[RecipeRead])
def list_recipes(
    service: RecipeServiceDep,
    title: Annotated[str | None, Query(description="Търсене по част от заглавието")] = None,
    category_id: Annotated[int | None, Query(description="Филтър по категория")] = None,
    max_prep_time: Annotated[
        int | None, Query(gt=0, description="Максимално време за приготвяне (включително), в минути")
    ] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return service.get_all(title, category_id, max_prep_time, skip, limit)


@router.post("/", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def create_recipe(data: RecipeCreate, service: RecipeServiceDep):
    return service.create(data)


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(recipe_id: int, service: RecipeServiceDep):
    return service.get_by_id(recipe_id)


@router.patch("/{recipe_id}", response_model=RecipeRead)
def update_recipe(recipe_id: int, data: RecipeUpdate, service: RecipeServiceDep):
    return service.update(recipe_id, data)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: int, service: RecipeServiceDep) -> None:
    service.delete(recipe_id)


@router.get("/{recipe_id}/scaled", response_model=RecipeScaledRead)
def get_scaled_recipe(
    recipe_id: int,
    service: RecipeServiceDep,
    servings: Annotated[
        int, Query(gt=0, le=MAX_SERVINGS, description=f"Желан брой порции (1–{MAX_SERVINGS})")
    ],
):
    return service.get_scaled(recipe_id, servings)


@router.get("/{recipe_id}/ingredients", response_model=list[RecipeIngredientRead])
def get_recipe_ingredients(recipe_id: int, service: RecipeServiceDep):
    return service.get_ingredients(recipe_id)


@router.post(
    "/{recipe_id}/ingredients",
    response_model=RecipeIngredientRead,
    status_code=status.HTTP_201_CREATED,
)
def add_recipe_ingredient(recipe_id: int, data: RecipeIngredientCreate, service: RecipeServiceDep):
    return service.add_ingredient(recipe_id, data)


@router.patch("/{recipe_id}/ingredients/{ingredient_id}", response_model=RecipeIngredientRead)
def update_recipe_ingredient(
    recipe_id: int, ingredient_id: int, data: RecipeIngredientUpdate, service: RecipeServiceDep
):
    return service.update_ingredient(recipe_id, ingredient_id, data)


@router.delete("/{recipe_id}/ingredients/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_recipe_ingredient(recipe_id: int, ingredient_id: int, service: RecipeServiceDep) -> None:
    service.remove_ingredient(recipe_id, ingredient_id)
