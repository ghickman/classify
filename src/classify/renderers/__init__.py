import enum

from .html import to_html
from .pager import to_pager


class Renderer(enum.StrEnum):
    HTML = enum.auto()
    PAGER = enum.auto()


__all__ = [
    "Renderer",
    "to_html",
    "to_pager",
]
