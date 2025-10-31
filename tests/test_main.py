from pathlib import Path

import pytest
from click.testing import CliRunner

from classify.main import run


@pytest.mark.parametrize(
    "invocation",
    [
        ["tests.dummy_class.DummyClass"],
        ["tests.dummy_class.DummyClass", "--renderer", "console"],
        [
            "tests.dummy_class.DummyClass",
            "--django-settings",
            "classify.contrib.django.settings",
        ],
    ],
    ids=["default-renderer", "django-settings", "console-renderer"],
)
def test_run(invocation):
    runner = CliRunner()

    result = runner.invoke(run, invocation)

    assert result.exit_code == 0
    assert "DummyClass" in result.output


def test_run_with_html_renderer():
    runner = CliRunner()

    result = runner.invoke(
        run,
        ["tests.dummy_class.DummyClass", "--renderer", "html"],
    )

    assert result.exit_code == 0
    assert result.output.startswith("Wrote:")


def test_run_with_html_renderer_and_output_set():
    runner = CliRunner()

    result = runner.invoke(
        run,
        [
            "tests.dummy_class.DummyClass",
            "--renderer",
            "html",
            "--output",
            "output",
        ],
    )

    assert result.exit_code == 0
    assert result.output == "Wrote: output/classify.html\n"

    output = Path("output/classify.html").read_text()
    assert "DummyClass" in output


def test_run_with_import_error():
    runner = CliRunner()

    result = runner.invoke(run, ["tests.import_error.Foo"])

    assert result.exit_code == 1
    assert result.output.startswith(
        "Could not import 'tests.import_error.Foo', the original error was:"
    )


def test_run_with_pager_renderer():
    runner = CliRunner()

    result = runner.invoke(run, ["tests.dummy_class.DummyClass", "--renderer", "pager"])

    assert result.exit_code == 0
    assert "DummyClass" in result.output


def test_run_with_unknown_path():
    runner = CliRunner()

    result = runner.invoke(run, ["unknown"])

    assert result.exit_code == 1
    assert result.output == "Could not import: unknown\n"


def test_run_without_a_class():
    runner = CliRunner()

    result = runner.invoke(run, ["tests.dummy_class"])

    assert result.exit_code == 1
    assert (
        result.output
        == "tests.dummy_class doesn't look like a class, please specify the path to a class\n"
    )
