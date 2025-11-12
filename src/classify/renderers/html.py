import contextlib
import functools
import inspect
import os
import socketserver
import tempfile
import webbrowser
from collections.abc import Generator
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

from ..library import Class


class Handler(SimpleHTTPRequestHandler):  # pragma: no cover
    def do_GET(self):
        self.path = "classify.html"
        return SimpleHTTPRequestHandler.do_GET(self)


def attribute_value(value):
    if isinstance(value, str):
        return f'"{value}"'

    if inspect.isclass(value):
        return value.__name__

    return value


@functools.singledispatch
@contextlib.contextmanager
def resolve_path(output_path: Path) -> Generator:
    output_path.mkdir(exist_ok=True)
    yield output_path


@resolve_path.register
@contextlib.contextmanager
def _(empty: None) -> Generator:  # noqa: ARG001
    directory = tempfile.TemporaryDirectory(prefix="classify")

    yield Path(directory.name)

    directory.cleanup()


def serve_output(port: int) -> None:  # pragma: no cover
    httpd = socketserver.TCPServer(("", port), Handler)

    if not os.environ.get("TEST_MODE", None):
        print(f"Serving on port: {port}")
        webbrowser.open_new_tab(f"http://localhost:{port}/")

    httpd.serve_forever()


def to_html(structure: Class, output_path: Path | None, serve: bool, port: int) -> None:
    from jinja2 import Environment, PackageLoader  # noqa: PLC0415

    env = Environment(loader=PackageLoader("classify", "templates"))
    env.filters["attribute"] = attribute_value
    template = env.get_template("web.html")
    output = template.render(klass=structure)

    with resolve_path(output_path) as path:
        full_path = path / "classify.html"
        full_path.write_text(output)

        if not serve:
            print(f"Wrote: {full_path}")
            return

        with contextlib.chdir(path):  # pragma: no cover
            serve_output(port)
