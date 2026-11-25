def not_blank(value: str | None) -> str:
    if value is None:
        raise ValueError("Полето не може да бъде null")
    value = value.strip()
    if not value:
        raise ValueError("Полето не може да бъде празно или да съдържа само интервали")
    return value


def optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None
