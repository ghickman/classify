import subprocess
import tempfile
import time
from pathlib import Path

import httpx
import pytest

from classify.renderers.html import resolve_path, to_html


class DummyClass:
    some_attr = 7

    def one(self):
        pass


@pytest.fixture(scope="session")
def classify_server():
    ds_proc = subprocess.Popen(
        [
            "classify",
            "tests.renderers.test_html.DummyClass",
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


def test_to_html(dummy_class):
    with tempfile.TemporaryDirectory() as path:
        path = Path(path)  # noqa: PLW2901
        to_html(dummy_class, output_path=path, serve=False, port=8000)

        output = path / "classify.html"
        assert output.exists()

        content = output.read_text()
        assert dummy_class.name in content


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
