import enum
from typing import TypeVar

E = TypeVar('E', bound=enum.Enum)

def enum_get(e: type[E], key, default: E) -> E:
    try:
        return e[key]
    except KeyError:
        return default
