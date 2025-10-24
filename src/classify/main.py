import collections
import os
import pydoc
import sys
from pathlib import Path

import click

from . import renderers
from .library import build
from .renderers import Renderer


@click.command()
@click.argument("klass")
@click.option("--django-settings", default="classify.contrib.django.settings")
@click.option(
    "--renderer",
    default=Renderer.PAGER,
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
def run(klass, django_settings, renderer: Renderer, output_path, port, serve) -> None:
    if django_settings:
        os.environ["DJANGO_SETTINGS_MODULE"] = django_settings

    try:
        structure = build(klass)
    except (ImportError, pydoc.ErrorDuringImport):
        sys.stderr.write(f"Could not import: {sys.argv[1]}\n")
        sys.exit(1)

    for name, lst in structure["attributes"].items():
        for i, definition in enumerate(lst):
            a = definition["defining_class"]
            structure["attributes"][name][i]["defining_class"] = a.__name__

            if isinstance(definition["object"], list):
                try:
                    s = f"[{', '.join([c.__name__ for c in definition['object']])}]"
                except AttributeError:
                    pass
                else:
                    structure["attributes"][name][i]["default"] = s
                    continue

    sorted_attributes = sorted(structure["attributes"].items(), key=lambda t: t[0])
    structure["attributes"] = collections.OrderedDict(sorted_attributes)

    sorted_methods = sorted(structure["methods"].items(), key=lambda t: t[0])
    structure["methods"] = collections.OrderedDict(sorted_methods)

    match renderer:
        case Renderer.HTML:
            renderers.to_html(structure, output_path, serve, port)
        case Renderer.PAGER:
            renderers.to_pager(structure)

    sys.exit(0)


if __name__ == "__main__":
    run()
