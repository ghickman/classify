import pytest

from classify.library import get_members

from .dummy_class import DummyClass, DummyParent


@pytest.mark.parametrize(
    ("cls", "expected"),
    [
        (DummyParent, ["__dict__", "__weakref__", "one", "three"]),
        (
            DummyClass,
            [
                "__init__",
                "class_method",
                "class_only_method",
                "four",
                "my_cached_prop",
                "my_dj_cached_prop",
                "my_property",
                "one",
                "some_attribute",
                "static_method",
                "two",
            ],
        ),
    ],
    ids=["parent", "child"],
)
def test_get_members(cls, expected):
    members = get_members(cls)

    names = [m.name for m in members]

    assert names == expected, names
