from rich.console import Console
from rich.syntax import Syntax

from .string import to_string


def to_console(structure, theme, console=None):
    if not console:
        console = Console()

    content = to_string(structure)
    syntax = Syntax(content, "python", theme=theme)
    console.print(syntax)


def to_pager(structure, theme):
    console = Console()
    with console.pager(styles=True):
        to_console(structure, theme, console=console)
