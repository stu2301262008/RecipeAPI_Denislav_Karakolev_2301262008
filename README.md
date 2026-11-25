# Recipe API

RESTful API за каталог с рецепти, автори, категории и съставки – **FastAPI + SQLAlchemy 2 + Pydantic v2 + Alembic + SQLite**.

## Стартиране

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head          # създава базата recipes.db чрез миграциите
uvicorn app.main:app --reload
```

Swagger документация: <http://127.0.0.1:8000/docs>

> Максималният брой порции при преизчисляване е `50 + 08 = 58` (факултетен номер 2301262008).

## Структура

```
app/
├── main.py            # създаване на FastAPI приложението, регистриране на рутери и error handlers
├── config.py          # настройки (DATABASE_URL, FACULTY_NUMBER, MAX_SERVINGS)
├── database.py        # engine, SessionLocal, Base (DeclarativeBase), get_db dependency
├── dependencies.py    # Dependency Injection – сесия и услуги (services)
├── exceptions.py      # NotFoundError / ConflictError + exception handlers
├── models/            # SQLAlchemy ORM модели (Mapped / mapped_column / relationship)
├── schemas/           # Pydantic схеми (Create / Update / Read) и валидации
├── services/          # бизнес логика и заявки към базата
└── routers/           # HTTP ендпойнти
alembic/versions/
├── 0001_initial_tables.py         # начални таблици
└── 0002_add_recipe_difficulty.py  # добавя задължително поле difficulty
```

## Ендпойнти

| Метод | Път | Описание |
|---|---|---|
| GET/POST | `/authors/` | списък / създаване |
| GET/PATCH/DELETE | `/authors/{id}` | четене / редакция / изтриване (409 ако има рецепти) |
| GET | `/authors/{id}/recipes` | рецепти на автор |
| GET/POST | `/categories/` | списък / създаване |
| GET/PATCH/DELETE | `/categories/{id}` | изтриването оставя рецептите без категория |
| GET | `/categories/{id}/recipes` | рецепти в категория |
| GET/POST | `/ingredients/` | списък / създаване |
| GET/PATCH/DELETE | `/ingredients/{id}` | изтриване – 409 ако участва в рецепта |
| GET | `/recipes/?title=&category_id=&max_prep_time=` | списък с филтри (AND) |
| POST | `/recipes/` | създаване |
| GET/PATCH/DELETE | `/recipes/{id}` | изтриването премахва връзките със съставките |
| GET | `/recipes/{id}/ingredients` | съставки с количество и мерна единица |
| POST | `/recipes/{id}/ingredients` | добавяне на съществуваща съставка (409 при повторение) |
| PATCH | `/recipes/{id}/ingredients/{ingredient_id}` | промяна на количество / мерна единица |
| DELETE | `/recipes/{id}/ingredients/{ingredient_id}` | премахване от рецептата (съставката остава) |
| GET | `/recipes/{id}/scaled?servings=N` | преизчислени количества (без запис в базата) |

## Правила при изтриване (на ниво база данни)

| Връзка | ON DELETE |
|---|---|
| `recipes.author_id → authors.id` | `RESTRICT` (+ проверка в услугата → 409) |
| `recipes.category_id → categories.id` | `SET NULL` |
| `recipe_ingredients.recipe_id → recipes.id` | `CASCADE` |
| `recipe_ingredients.ingredient_id → ingredients.id` | `RESTRICT` (+ проверка в услугата → 409) |

За SQLite ограниченията на външните ключове се включват с `PRAGMA foreign_keys=ON` при всяка връзка (`app/database.py`).
