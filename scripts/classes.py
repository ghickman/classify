#!/usr/bin/env python

import ast
import importlib
import itertools
import os
from collections.abc import Iterator
from pathlib import Path

import click
import django


class ClassFinder(ast.NodeVisitor):
    """AST visitor that extracts class definitions from Python source."""

    def __init__(self, path: str, module_path: str):
        self.path = path
        self.module_path = module_path
        self.classes: list[ast.ClassDef] = []
        self._in_class: bool = False

    def visit_ClassDef(self, node: ast.ClassDef):
        if self._in_class:
            return

        self.classes.append(f"{self.module_path}.{node.name}")

        self._in_class = True
        self.generic_visit(node)
        self._in_class = False


def dotted_path(path: Path, root: Path, prefix: str) -> str:
    """Convert a file path to a dotted module path rooted at `prefix`."""
    rel_path = path.relative_to(root)

    parts = list(rel_path.parts)
    if parts[-1] == "__init__.py":
        parts = parts[:-1]
    elif parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]

    suffix = ".".join(parts)
    return f"{prefix}.{suffix}" if suffix else prefix


def iter_classes(path: Path, root: Path, prefix: str) -> Iterator[str]:
    """Parse a Python file and extract all class definitions."""
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, UnicodeDecodeError) as e:
        click.echo(f"Warning: Could not parse {path}: {e}", err=True)
        return []

    module_path = dotted_path(path, root, prefix)
    finder = ClassFinder(str(path), module_path)
    finder.visit(tree)
    yield from finder.classes


def iter_files(root: Path) -> Iterator[Path]:
    """Recursively find all Python files in a directory."""
    for path in root.rglob("*.py"):
        if not any(part.startswith(".") for part in path.relative_to(root).parts):
            yield path


@click.command()
@click.argument("package")
@click.option("--django-settings")
def cli(package, django_settings):
    if django_settings:
        os.environ["DJANGO_SETTINGS_MODULE"] = django_settings
        django.setup()

    module = importlib.import_module(package)
    package_path = Path(module.__path__[0])

    files = iter_files(package_path)
    classes = list(
        itertools.chain.from_iterable(
            iter_classes(f, package_path, package) for f in files
        )
    )
    for cls_path in classes:
        click.echo(cls_path)


if __name__ == "__main__":
    cli()
