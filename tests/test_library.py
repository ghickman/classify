import pytest

from classify.library import get_members

from .dummy_class import DummyClass, DummyParent


@pytest.mark.parametrize(
    ("cls", "expected"),
    [
        (DummyParent, ["__dict__", "__weakref__", "one", "three"]),
        (DummyClass, ["__init__", "one", "two"]),
    ],
    ids=["parent", "child"],
)
def test_get_members(cls, expected):
    members = get_members(cls)

    names = [m[0] for m in members]

    assert names == expected, names
