import logging
import pydoc
import sys
from pathlib import Path

import click
import structlog
from rich.syntax import DEFAULT_THEME

from . import renderers
from .classification import classify
from .django import setup_django
from .exceptions import NotAClassError
from .hooks import NO_HOOKS
from .renderers import Renderer
from .resolution import resolve


@click.command()
@click.argument("klass")
@click.option(
    "--console-theme",
    default=DEFAULT_THEME,
    help="Theme to render console output with, any Pygments style works here",
    show_default=True,
)
@click.option("--debug", is_flag=True, help="Show debug logs")
@click.option(
    "--django-settings",
    help="Pass a dotted path to your Django settings when using with a Django project.  classify.contrib.django.settings exists if you need it.",
)
@click.option(
    "--renderer",
    default=Renderer.CONSOLE.value,
    type=click.Choice(Renderer, case_sensitive=False),
    help="How would you like your content rendered?",
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    "output_path",
    default=None,
    type=click.Path(file_okay=False, path_type=Path),
    help="Path for output files to be saved",
)
@click.option(
    "-p",
    "--port",
    default=8000,
    type=click.INT,
    help="The port to serve content at, requires --serve",
    show_default=True,
)
@click.option(
    "-s",
    "--serve",
    is_flag=True,
    help="Serve HTML content, requires --renderer=html",
)
@click.version_option()
def run(
    klass,
    console_theme,
    debug,
    django_settings,
    renderer: Renderer,
    output_path,
    port,
    serve,
) -> None:
    """
    See everything a Python class inherits, and the code behind it.
    """
    hooks = NO_HOOKS
    if django_settings:
        setup_django(django_settings)

        # import after configuring Django, and in this branch so we classify
        # doesn't have to have Django as a dependency
        from .contrib.django.hooks import hooks  # noqa: PLC0415

    default_log_level = logging.DEBUG if debug else logging.WARNING
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(default_log_level),
    )

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

    structure = classify(obj, hooks=hooks)

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
