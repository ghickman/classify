#!/usr/bin/env python

import logging
import sys
from collections import defaultdict
from pathlib import Path

import click
import structlog

from classify.classification import classify
from classify.django import setup_django
from classify.resolution import resolve


structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.WARNING),
)


def write_failures(failures: dict[str, list[str]], output_path: Path) -> None:
    sections = []

    for error_type in sorted(failures):
        classes = sorted(failures[error_type])
        body = "\n".join(f"- {c}" for c in classes)
        sections.append(f"## {error_type} ({len(classes)})\n{body}")

    content = "\n\n".join(sections)
    if content:
        content += "\n"
    output_path.write_text(content)


@click.command()
@click.option("--django-settings")
@click.option(
    "--output",
    "output_path",
    default="failures.md",
    type=click.Path(path_type=Path),
)
def cli(django_settings, output_path):
    if django_settings:
        setup_django(django_settings)

    failures: dict[str, list[str]] = defaultdict(set)

    for line in sys.stdin:
        class_path = line.strip()
        if not class_path:
            continue

        try:
            classify(resolve(class_path))
        except Exception as exc:  # noqa: BLE001
            error_type = type(exc).__name__
            failures[error_type].add(class_path)

    write_failures(failures, output_path)


if __name__ == "__main__":
    cli()
