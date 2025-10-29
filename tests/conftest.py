import pytest

from classify.library import Class, Line, Method


def method(name, **kwargs):
    return Method(
        name=name,
        docstring=kwargs.get("docstring", ""),
        defining_class=kwargs.get("defining_class", ""),
        arguments=kwargs.get("arguments", ""),
        code=kwargs.get("code", ""),
        lines=Line(start=42, total=7),
    )


@pytest.fixture
def dummy_class():
    return Class(
        name="MyClass",
        methods={
            "one": [
                method("one", defining_class="ParentClass"),
                method("one", defining_class="MyClass"),
            ]
        },
        docstring="",
        ancestors=[],
        parents=["ParentClass"],
        attributes={},
    )
