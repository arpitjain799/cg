"""Enum classes has string or list values that behaves like defined """
from enum import Enum


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return str.__str__(self)


class ListEnum(list, Enum):
    pass


class IntEnum(int, Enum):
    def __int__(self) -> int:
        return int.__int__(self)
