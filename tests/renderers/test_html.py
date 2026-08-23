import subprocess
import tempfile
import time
from pathlib import Path

import httpx
import pytest

from classify.renderers.html import resolve_path, to_html


@pytest.fixture(scope="session")
def classify_server():
    ds_proc = subprocess.Popen(
        [
            "classify",
            "tests.dummy_class.DummyClass",
            "--renderer",
            "html",
            "--serve",
            "--port",
            "8008",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    # Give the server time to start
    time.sleep(1)

    # Check it started successfully
    assert not ds_proc.poll(), ds_proc.stdout.read().decode("utf-8")

    yield ds_proc

    # Shut it down at the end of the pytest session
    ds_proc.terminate()


@pytest.fixture
def rendered(dummy_class):
    with tempfile.TemporaryDirectory() as path:
        to_html(dummy_class, output_path=Path(path), serve=False, port=8000)

        yield (Path(path) / "classify.html").read_text()


def test_to_html(dummy_class):
    with tempfile.TemporaryDirectory() as path:
        path = Path(path)  # noqa: PLW2901
        to_html(dummy_class, output_path=path, serve=False, port=8000)

        output = path / "classify.html"
        assert output.exists()

        content = output.read_text()
        assert dummy_class.name in content


def test_to_html_escapes_content(rendered):
    assert "return 1 &lt; 2" in rendered
    assert "return 1 < 2" not in rendered

    assert "my_var = &#34;a&lt;b&#34;" in rendered
    assert 'my_var = "a<b"' not in rendered


def test_to_html_renders_ancestors(rendered):
    assert "<li>tests.ParentClass</li>" in rendered


def test_to_html_renders_attribute_defining_class(rendered):
    assert "<td>tests.MyClass</td>" in rendered


def test_to_html_renders_method_defining_class(rendered):
    assert "def one: [ParentClass]" in rendered
    assert "def one: [MyClass]" in rendered


def test_to_html_renders_method_line_range(rendered):
    # a method starting on line 42 with 7 lines ends on line 48
    assert "Found on lines 42 to 48 of" in rendered


def test_to_html_and_serve(classify_server):  # noqa: ARG001
    response = httpx.get("http://127.0.0.1:8008/")
    assert response.status_code == 200  # noqa: PLR2004


def test_resolve_path_with_path():
    with tempfile.TemporaryDirectory() as parent:
        path = Path(parent) / "testing"
        assert not path.exists()

        with resolve_path(path) as made_path:
            assert made_path == path
            assert made_path.exists()


def test_resolve_path_without_path():
    with resolve_path(None) as path:
        assert path.exists()

    assert not path.exists()
