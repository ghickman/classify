# list available commands
default:
    @{{ just_executable() }} --list

format *args:
    uv run ruff format {{ args }}

lint *args:
    uv run ruff check {{ args }}

toml-sort *args:
    uv run toml-sort {{ args }} pyproject.toml

type-check *args:
    uv run ty check

check:
    {{ just_executable() }} format --check
    {{ just_executable() }} lint
    {{ just_executable() }} toml-sort --check
    {{ just_executable() }} type-check

fix:
    {{ just_executable() }} format
    {{ just_executable() }} lint --fix
    {{ just_executable() }} toml-sort --in-place

release:
    uv build
    uv publish

run *args="":
    uv run classify {{ args }}

@console:
    just run django.views.generic.FormView --console-theme dracula

@html:
    just run django.views.generic.FormView --renderer html --output output

test *args="":
    uv run -m coverage run --module pytest tests {{ args }}
    -uv run -m coverage report
    uv run -m coverage html

e2e *args="--console-theme dracula":
    classify tests.dummy_class.DummyClass --django-settings classify.contrib.django.settings {{ args }}

find-classes path settings="":
    #!/bin/bash
    set -u

    class_paths=$(scripts/classes.py {{ path }} --django-settings {{ settings }})
    while read path; do
        classify --django-settings {{ settings }} "$path" > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo $path
            continue
        fi
    done <<< "$class_paths"
