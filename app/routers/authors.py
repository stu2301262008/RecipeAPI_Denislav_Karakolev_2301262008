from typing import Annotated

from fastapi import APIRouter, Query, status

from app.dependencies import AuthorServiceDep
from app.schemas.author import AuthorCreate, AuthorRead, AuthorUpdate
from app.schemas.recipe import RecipeRead

router = APIRouter(prefix="/authors", tags=["Authors"])


@router.get("/", response_model=list[AuthorRead])
def list_authors(
    service: AuthorServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
):
    return service.get_all(skip, limit)


@router.post("/", response_model=AuthorRead, status_code=status.HTTP_201_CREATED)
def create_author(data: AuthorCreate, service: AuthorServiceDep):
    return service.create(data)


@router.get("/{author_id}", response_model=AuthorRead)
def get_author(author_id: int, service: AuthorServiceDep):
    return service.get_by_id(author_id)


@router.patch("/{author_id}", response_model=AuthorRead)
def update_author(author_id: int, data: AuthorUpdate, service: AuthorServiceDep):
    return service.update(author_id, data)


@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(author_id: int, service: AuthorServiceDep) -> None:
    service.delete(author_id)


@router.get("/{author_id}/recipes", response_model=list[RecipeRead])
def get_author_recipes(author_id: int, service: AuthorServiceDep):
    return service.get_recipes(author_id)
