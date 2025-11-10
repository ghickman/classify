import pytest

from classify.library import Attribute, Class, Line, Method


def inner_class(name):
    return Class(
        name=name,
        docstring="",
        ancestors=[name],
        parents=[],
        attributes={
            "abc": [
                Attribute(
                    name="abc",
                    object="123",
                    defining_class=name,
                    value="123",
                )
            ]
        },
        classes=[],
        methods={},
    )


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
        docstring="",
        ancestors=[],
        parents=["ParentClass"],
        attributes={},
        classes=[
            inner_class("Meta"),
        ],
        methods={
            "one": [
                method("one", defining_class="ParentClass"),
                method("one", defining_class="MyClass"),
            ]
        },
    )
