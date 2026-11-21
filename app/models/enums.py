import enum


class Unit(str, enum.Enum):
    g = "g"
    ml = "ml"
    pcs = "pcs"


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
