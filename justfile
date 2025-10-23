black *args="":
    uv run black --check src {{ args }}

ruff *args="":
    uv run ruff check {{ args }}

toml-sort *args:
    uv run toml-sort {{ args }} pyproject.toml

check: black ruff
    {{ just_executable() }} toml-sort --check

fix:
    uv run black src
    uv run ruff check --fix src
    {{ just_executable() }} toml-sort --in-place

release:
    uv build
    uv publish

run *args="":
    classify {{ args }}
