import pytest

from classify.library import Attribute, SimpleClass
from classify.renderers.string import attributes, docstring


class MyClass:
    pass


@pytest.mark.parametrize(
    ("attr", "expected"),
    [
        (
            Attribute(
                name="my_var",
                defining_class=SimpleClass(name="MyClass", module=""),
                value="test",
            ),
            'my_var = "test"\n',
        ),
        (
            Attribute(
                name="my_var",
                defining_class=SimpleClass(name="MyClass", module=""),
                value=MyClass,
            ),
            "my_var = MyClass\n",
        ),
        (
            Attribute(
                name="my_var",
                defining_class=SimpleClass(name="MyClass", module=""),
                value=7,
            ),
            "my_var = 7\n",
        ),
    ],
    ids=["string", "class", "int"],
)
def test_attributes(attr, expected):
    assert attributes({"my_var": [attr]}, indent="") == expected


def test_docstring():
    assert docstring("", indent="    ") == ""
