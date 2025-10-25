import enum

from .console import to_console, to_pager
from .html import to_html
from .string import to_string


class Renderer(enum.StrEnum):
    CONSOLE = enum.auto()
    HTML = enum.auto()
    PAGER = enum.auto()
    STRING = enum.auto()


__all__ = [
    "Renderer",
    "to_console",
    "to_html",
    "to_pager",
    "to_string",
]
