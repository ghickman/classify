black *args="":
    uv run black --check classify {{ args }}

fix:
    uv run black classify

release:
    uv run setup.py register sdist upload
    uv run setup.py register bdist_wheel upload
