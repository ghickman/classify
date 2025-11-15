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
                "Meta",
                "__init__",
                "class_method",
                "class_only_method",
                "four",
                "my_cached_prop",
                "my_class",
                "my_dj_cached_prop",
                "my_int",
                "my_prop",
                "my_string",
                "one",
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
