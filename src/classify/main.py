import collections
import os
import pydoc
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import click
from jinja2 import Environment, PackageLoader

from .formatters import html, paged
from .library import build


def serve_output(port: int) -> None:
    httpd = HTTPServer(("", port), BaseHTTPRequestHandler)
    print(f"Serving on port: {port}")
    webbrowser.open_new_tab(f"http://localhost:{port}/output/classify.html")
    httpd.serve_forever()


@click.command()
@click.argument("klass")
@click.option("--django", "use_django", is_flag=True)
@click.option("--django-settings")
@click.option("--html", "render_to_html", is_flag=True)
@click.option(
    "-o",
    "--output",
    "output_path",
    default="output",
    type=click.Path(file_okay=False, path_type=Path),
    help="Relative path for output files to be saved",
)
@click.option("-p", "--port", default=8000, type=click.INT)
@click.option("-s", "--serve", is_flag=True)
def run(
    klass,
    use_django,
    django_settings,
    render_to_html,
    output_path,
    port,
    serve,
) -> None:
    if use_django:
        os.environ["DJANGO_SETTINGS_MODULE"] = "classify.contrib.django.settings"

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

    env = Environment(loader=PackageLoader("classify", "templates"))
    if render_to_html:
        template = env.get_template("web.html")
        output = html(structure, template)

        output_path.mkdir(exist_ok=True)
        (output_path / "classify.html").write_text(output)

        if serve:
            serve_output(port)
    else:
        pydoc.pager(paged(structure))

    sys.exit(0)


if __name__ == "__main__":
    run()
