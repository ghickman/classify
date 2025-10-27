import pytest

from classify.library import get_members


class DummyParent:
    def one(self):
        print("one parent")

    def three(self):
        pass


class DummyClass(DummyParent):
    def __init__(self):
        super().__init__()

    def _internal(self):
        pass

    def one(self):
        super().one()
        print("one child")

    def two(self):
        pass


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
