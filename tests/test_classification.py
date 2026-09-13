import datetime

import pytest

from classify import classification
from classify.classification import bucket_for, bucket_members, classify, get_members
from classify.dataclasses import Bucket, Member

from .dummy_class import DummyClass, DummyEnum, DummyParent


class DictSubclass(dict):
    def mine(self): ...


# classes to test against, covering a seletion of Python, C, and some
# edge-casey ones
CORPUS = [
    DummyParent,
    DummyClass,
    DummyEnum,
    DictSubclass,
    int,
    datetime.datetime,
]


def member_named(cls, name) -> Member:
    return next(m for m in get_members(cls) if m.name == name)


@pytest.mark.parametrize(
    ("cls", "name", "expected"),
    [
        (DummyClass, "my_int", Bucket.ATTRIBUTE),
        (DummyClass, "my_class", Bucket.ATTRIBUTE),
        (DummyClass, "Meta", Bucket.CLASS),
        (DummyClass, "one", Bucket.METHOD),
        (DummyClass, "four", Bucket.METHOD),
        (DummyClass, "my_cached_prop", Bucket.METHOD),
        (DummyClass, "my_prop", Bucket.PROPERTY),
        (DummyClass, "my_data_descriptor", Bucket.DATA_DESCRIPTOR),
        (DummyParent, "__dict__", Bucket.NATIVE),
        (DummyParent, "__weakref__", Bucket.NATIVE),
        (DictSubclass, "mine", Bucket.METHOD),
        (int, "bit_length", Bucket.NATIVE),
        (int, "from_bytes", Bucket.NATIVE),
        (int, "real", Bucket.NATIVE),
    ],
)
def test_bucket_for(cls, name, expected):
    assert bucket_for(member_named(cls, name)) == expected


def test_bucket_for_unknown_kind():
    # pydoc never emits "property", it rewrites property objects to "data
    # descriptor" or "readonly property", so this acts like an unknown member
    # to check that path works
    member = Member(name="mystery", kind="property", cls=DummyClass, obj=None)

    assert bucket_for(member) == Bucket.UNKNOWN


@pytest.mark.parametrize("cls", CORPUS, ids=lambda c: c.__name__)
def test_bucket_members_leaves_nothing_behind(cls):
    members = get_members(cls)

    buckets = bucket_members(members)
    names = {m.name for members in buckets.values() for m in members}

    assert names == {m.name for m in members}


@pytest.mark.parametrize("cls", CORPUS, ids=lambda c: c.__name__)
def test_bucket_members_has_no_unknowns(cls):
    # pydoc's kinds are a fixed set, so anything landing here means the
    # vocabulary has changed under us
    buckets = bucket_members(get_members(cls))

    assert buckets[Bucket.UNKNOWN] == []


def test_bucket_members_seeds_every_bucket():
    buckets = bucket_members([])

    assert sorted(buckets) == sorted(Bucket)


def test_enums():
    structure = classify(DummyEnum)

    # sense check, but the main point here is to check an Enum is correctly
    # classified
    assert structure.name == "DummyEnum"


def test_classify_correctly_buckets_members():
    data = classify(DummyClass)

    assert set(data.attributes.keys()) == {
        "my_class",
        "my_int",
        "my_string",
    }

    assert {c.name for c in data.classes} == {
        "Meta",
    }

    assert set(data.properties.keys()) == {
        "my_prop",
        "my_cached_prop",
        "my_dj_cached_prop",
    }

    assert set(data.methods.keys()) == {
        "one",
        "two",
        "three",
        "four",
        "__init__",
        "class_method",
        "class_only_method",
        "static_method",
    }

    assert data.data_descriptors.keys() == {
        "my_data_descriptor",
    }


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


@pytest.mark.parametrize(
    "cls",
    [DummyParent, DummyClass, DummyEnum, int, datetime.datetime],
    ids=lambda c: c.__name__,
)
def test_classify_has_no_unknown_members(cls):
    assert classify(cls).unknown == {}


def test_classify_records_native_members():
    structure = classify(DummyParent)

    assert "__dict__" in structure.native
    assert "__weakref__" in structure.native

    descriptor = structure.native["__dict__"][-1]
    assert descriptor.kind == "data descriptor"
    assert descriptor.type_name == "getset_descriptor"
    assert descriptor.defining_class.name == "DummyParent"


def test_classify_records_unknown_members(monkeypatch):
    # test the unknown path for bucketing, even though pydoc doesn't actually
    # give us a kind that lets us get there currently
    class Mystery:
        pass

    member = Member(name="mystery", kind="property", cls=Mystery, obj=None)

    def with_unknown(members):
        buckets = bucket_members(members)
        buckets[Bucket.UNKNOWN].append(member)
        return buckets

    # don't love it, but needs must
    monkeypatch.setattr(classification, "bucket_members", with_unknown)

    structure = classify(Mystery)

    assert "mystery" in structure.unknown
    assert structure.unknown["mystery"][-1].type_name == "NoneType"


def test_classify_treats_c_implemented_methods_as_native():
    class MyDict(dict):
        def mine(self): ...

    structure = classify(MyDict)

    assert "mine" in structure.methods
    for name in ["get", "fromkeys", "__getitem__"]:
        assert name not in structure.methods
        assert name in structure.native


def test_classify_classes_have_line_numbers():
    structure = classify(DummyClass)

    assert structure.lines
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
