import pytest

from classify.dataclasses import Attribute, Class, Line, Method, SimpleClass
from classify.django import setup_django


@pytest.fixture(scope="module")
def setup_dj():
    setup_django("tests.django_proj.core.settings")


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
        lines=Line(source="", start=42, total=7),
    )


def method(name, **kwargs):
    defining_class = kwargs.get("defining_class", SimpleClass(name="", module=""))

    return Method(
        name=name,
        docstring=kwargs.get("docstring", ""),
        defining_class=defining_class,
        arguments=kwargs.get("arguments", ""),
        code=kwargs.get("code", ""),
        lines=Line(source="", start=42, total=7),
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
        lines=Line(source="", start=42, total=7),
    )
