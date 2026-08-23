import pytest

from classify.dataclasses import Attribute, Class, Line, Method, SimpleClass


class ParentClass:
    pass


def inner_class(name):
    return Class(
        name=name,
        module="",
        docstring="",
        ancestors=[],
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
        data_descriptors={},
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
        ancestors=[SimpleClass(name="ParentClass", module="tests")],
        parents=[ParentClass],
        attributes={
            "my_var": [
                Attribute(
                    name="my_var",
                    defining_class=SimpleClass(name="MyClass", module="tests"),
                    value="a<b",
                )
            ]
        },
        classes=[
            inner_class("Meta"),
        ],
        properties={},
        data_descriptors={},
        methods={
            "one": [
                method(
                    "one", defining_class=SimpleClass(name="ParentClass", module="")
                ),
                method(
                    "one",
                    defining_class=SimpleClass(name="MyClass", module=""),
                    code="    def one(self):\n        return 1 < 2\n",
                ),
            ]
        },
    )
