import pytest

from classify.classification import classify, get_members

from .dummy_class import DummyClass, DummyEnum, DummyParent


def test_enums():
    structure = classify(DummyEnum)

    # sense check, but the main point here is to check an Enum is correctly
    # classified
    assert structure.name == "DummyEnum"


@pytest.mark.parametrize(
    "name",
    [
        "class_method",
        "class_only_method",
        "my_cached_prop",
        "my_dj_cached_prop",
        "static_method",
    ],
)
def test_classify_includes_wrapped_methods(name):
    # only include wrapped methods which are defined in Python so we can get
    # their source
    structure = classify(DummyClass)

    assert name in structure.methods


def test_classify_excludes_c_implemented_methods():
    class MyDict(dict):
        def mine(self): ...

    structure = classify(MyDict)

    # drop methods defined in C, they have no source to render
    assert "mine" in structure.methods
    assert "get" not in structure.methods
    assert "fromkeys" not in structure.methods
    assert "__getitem__" not in structure.methods


def test_classify_classes_have_line_numbers():
    structure = classify(DummyClass)

    assert structure.lines.start == 49  # noqa: PLR2004
    assert structure.lines.total == 63  # noqa: PLR2004


@pytest.mark.parametrize(
    ("cls", "expected"),
    [
        (
            DummyParent,
            [
                "__dict__",
                "__weakref__",
                "my_data_descriptor",
                "my_prop",
                "one",
                "three",
            ],
        ),
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
                "my_data_descriptor",
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
