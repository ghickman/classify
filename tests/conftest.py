import pytest

from classify.library import Attribute, Class, Line, Method, SimpleClass


def inner_class(name):
    return Class(
        name=name,
        module="",
        docstring="",
        ancestors=[name],
        parents=[],
        attributes={
            "abc": [
                Attribute(
                    name="abc",
                    defining_class=SimpleClass(name=name, module=""),
                    value="123",
                )
            ]
        },
        classes=[],
        properties={},
        methods={},
    )


def method(name, **kwargs):
    defining_class = SimpleClass(name=kwargs.get("defining_class", ""), module="")

    return Method(
        name=name,
        docstring=kwargs.get("docstring", ""),
        defining_class=defining_class,
        arguments=kwargs.get("arguments", ""),
        code=kwargs.get("code", ""),
        lines=Line(start=42, total=7),
    )


@pytest.fixture
def dummy_class():
    return Class(
        name="MyClass",
        module="",
        docstring="",
        ancestors=[],
        parents=["ParentClass"],
        attributes={},
        classes=[
            inner_class("Meta"),
        ],
        properties={},
        methods={
            "one": [
                method(
                    "one", defining_class=SimpleClass(name="ParentClass", module="")
                ),
                method("one", defining_class=SimpleClass(name="MyClass", module="")),
            ]
        },
    )
