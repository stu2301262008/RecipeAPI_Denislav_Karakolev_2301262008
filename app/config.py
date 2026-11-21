import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(BASE_DIR / 'recipes.db').as_posix()}")

FACULTY_NUMBER = "2301262008"

MAX_SERVINGS = 50 + int(FACULTY_NUMBER[-2:])
