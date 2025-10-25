import contextlib
import functools
import socketserver
import tempfile
import webbrowser
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from types import GeneratorType


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.path = "classify.html"
        return SimpleHTTPRequestHandler.do_GET(self)


@functools.singledispatch
@contextlib.contextmanager
def resolve_path(output_path: Path) -> GeneratorType[Path]:
    output_path.mkdir(exist_ok=True)
    yield output_path


@resolve_path.register
@contextlib.contextmanager
def _(empty: None) -> GeneratorType[Path]:  # noqa: ARG001
    directory = tempfile.TemporaryDirectory(prefix="classify")

    yield Path(directory.name)

    directory.cleanup()


def serve_output(port: int) -> None:
    httpd = socketserver.TCPServer(("", port), Handler)

    print(f"Serving on port: {port}")
    webbrowser.open_new_tab(f"http://localhost:{port}/")
    httpd.serve_forever()


def to_html(structure, output_path: Path | None, serve: bool, port: int) -> None:
    from jinja2 import Environment, PackageLoader  # noqa: PLC0415

    env = Environment(loader=PackageLoader("classify", "templates"))
    template = env.get_template("web.html")
    output = template.render(klass=structure)

    with resolve_path(output_path) as path:
        full_path = path / "classify.html"
        full_path.write_text(output)

        if not serve:
            print(f"Wrote: {full_path}")
            return

        with contextlib.chdir(path):
            serve_output(port)
