import pydoc
import sys
from pathlib import Path

import click
from rich.syntax import DEFAULT_THEME

from . import renderers
from .django import setup_django
from .exceptions import NotAClassError
from .library import classify, resolve
from .renderers import Renderer


@click.command()
@click.argument("klass")
@click.option(
    "--console-theme",
    default=DEFAULT_THEME,
    help="Pygments theme to render console output with",
)
@click.option("--django-settings")
@click.option(
    "--renderer",
    default=Renderer.CONSOLE,
    type=click.Choice(Renderer, case_sensitive=False),
)
@click.option(
    "-o",
    "--output",
    "output_path",
    default=None,
    type=click.Path(file_okay=False, path_type=Path),
    help="Relative path for output files to be saved",
)
@click.option("-p", "--port", default=8000, type=click.INT)
@click.option("-s", "--serve", is_flag=True)
@click.version_option()
def run(
    klass, console_theme, django_settings, renderer: Renderer, output_path, port, serve
) -> None:
    if django_settings:
        setup_django(django_settings)

    try:
        obj = resolve(klass)
    except ImportError:
        click.echo(f"Could not import: {klass}", err=True)
        sys.exit(1)
    except pydoc.ErrorDuringImport as e:
        click.echo(
            f"Could not import '{klass}', the original error was:\n {e}", err=True
        )
        sys.exit(1)
    except NotAClassError:
        click.echo(
            f"{klass} doesn't look like a class, please specify the path to a class",
            err=True,
        )
        sys.exit(1)

    structure = classify(obj)

    match renderer:
        case Renderer.CONSOLE:
            renderers.to_console(structure, console_theme)
        case Renderer.HTML:
            renderers.to_html(structure, output_path, serve, port)
        case Renderer.PAGER:  # pragma: no branch
            # unclear why coverage thinks run() doesn't return, so marking as
            # no branch for now
            renderers.to_pager(structure, console_theme)


if __name__ == "__main__":  # pragma: no cover
    run()
