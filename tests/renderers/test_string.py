import pytest

from classify.dataclasses import Attribute, DataDescriptor, Method, SimpleClass
from classify.renderers.string import attributes, data_descriptors, docstring


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


def test_data_descriptors_without_deleter():
    class WithSetter:
        @property
        def value(self): ...

        @value.setter
        def value(self, value): ...

    prop = vars(WithSetter)["value"]
    descriptor = DataDescriptor(
        name="value",
        getter=Method.from_func(prop.fget, WithSetter),
        setter=Method.from_func(prop.fset, WithSetter),
        deleter=None,
    )

    output = data_descriptors({"value": [descriptor]}, indent="")

    assert "def value(self):" in output
    assert "@value.setter" in output


def test_docstring():
    assert docstring("", indent="    ") == ""
