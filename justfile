black *args="":
    uv run black --check src {{ args }}

fix:
    uv run black src

release:
    uv build
    uv publish

run *args="":
    classify {{ args }}
