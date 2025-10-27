import os
import pydoc
import sys
from pathlib import Path

import click
from rich.syntax import DEFAULT_THEME

from . import renderers
from .library import build
from .renderers import Renderer


@click.command()
@click.argument("klass")
@click.option(
    "--console-theme",
    default=DEFAULT_THEME,
    help="Pygments theme to render console output with",
)
@click.option("--django-settings", default="classify.contrib.django.settings")
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
        os.environ["DJANGO_SETTINGS_MODULE"] = django_settings

    try:
        structure = build(klass)
    except (ImportError, pydoc.ErrorDuringImport):
        sys.stderr.write(f"Could not import: {sys.argv[1]}\n")
        sys.exit(1)

    match renderer:
        case Renderer.CONSOLE:
            renderers.to_console(structure, console_theme)
        case Renderer.HTML:
            renderers.to_html(structure, output_path, serve, port)
        case Renderer.PAGER:
            renderers.to_pager(structure, console_theme)

    sys.exit(0)


if __name__ == "__main__":
    run()
