from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import CategoryServiceDep
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.recipe import RecipeRead

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(
    service: CategoryServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return service.get_all(skip, limit)


@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, service: CategoryServiceDep):
    return service.create(data)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, service: CategoryServiceDep):
    return service.get_by_id(category_id)


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(category_id: int, data: CategoryUpdate, service: CategoryServiceDep):
    return service.update(category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, service: CategoryServiceDep) -> None:
    service.delete(category_id)


@router.get("/{category_id}/recipes", response_model=list[RecipeRead])
def get_category_recipes(category_id: int, service: CategoryServiceDep):
    return service.get_recipes(category_id)
