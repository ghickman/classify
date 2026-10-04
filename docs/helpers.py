import os
import subprocess
from pathlib import Path


def cli(*args: str, columns: int = 100, language: str) -> str:
    """Get the output of a CLI command"""
    return block(run(*args, columns=columns), language=language)


def block(lines: list[str], language: str) -> str:
    """Wrap the given lines in a Markdown code block"""
    body = "".join([f"{line}\n" for line in lines])
    return f"```{language}\n{body}```\n"


def members(*args: str, columns: int = 100) -> str:
    """
    Limit the given lines to just class attributes

    Primarily used for Django models which inherit a lot of methods from
    models.Model.
    """
    lines = run(*args, columns=columns)

    end = next(
        i for i, line in enumerate(lines) if line.startswith(("    class ", "    def "))
    )

    return block(
        [*lines[:end], f"    # ... {len(lines[end:])} more lines"],
        language="python",
    )


def run(*args: str, columns: int = 100) -> list[str]:
    """Run a command and return its output as lines"""
    env = os.environ | {
        # Rich pads each line based on the console it was called in, we set
        # this to keep things consistent across runs
        "COLUMNS": str(columns),
        # Set because --django-settings imports the settings module before
        # we've put the working directory on sys.path.
        # TODO: handle this inside classify proper
        "PYTHONPATH": ".",
    }
    output = subprocess.run(
        args,
        check=True,
        env=env,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout

    return [line.rstrip() for line in output.splitlines()]


def source(path: str) -> str:
    """Get the contents of a Python file"""
    return block(
        Path(path).read_text().splitlines(),
        language="python",
    )
