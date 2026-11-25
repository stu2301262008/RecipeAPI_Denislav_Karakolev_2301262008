from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import IngredientServiceDep
from app.schemas.ingredient import IngredientCreate, IngredientRead, IngredientUpdate

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])


@router.get("/", response_model=list[IngredientRead])
def list_ingredients(
    service: IngredientServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return service.get_all(skip, limit)


@router.post("/", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
def create_ingredient(data: IngredientCreate, service: IngredientServiceDep):
    return service.create(data)


@router.get("/{ingredient_id}", response_model=IngredientRead)
def get_ingredient(ingredient_id: int, service: IngredientServiceDep):
    return service.get_by_id(ingredient_id)


@router.patch("/{ingredient_id}", response_model=IngredientRead)
def update_ingredient(ingredient_id: int, data: IngredientUpdate, service: IngredientServiceDep):
    return service.update(ingredient_id, data)


@router.delete("/{ingredient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingredient(ingredient_id: int, service: IngredientServiceDep) -> None:
    service.delete(ingredient_id)
