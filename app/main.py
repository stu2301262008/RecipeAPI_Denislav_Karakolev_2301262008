from fastapi import FastAPI

from app.exceptions import register_exception_handlers
from app.routers import authors, categories, ingredients, recipes

app = FastAPI(
    title="Recipe API",
    description="RESTful API за каталог с рецепти, автори, категории и съставки.",
    version="1.0.0",
)

register_exception_handlers(app)

app.include_router(authors.router)
app.include_router(categories.router)
app.include_router(ingredients.router)
app.include_router(recipes.router)


@app.get("/", tags=["Root"])
def root() -> dict[str, str]:
    return {"message": "Recipe API – документация на /docs"}
