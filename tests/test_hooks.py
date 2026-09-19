import pytest
from first import first

from classify.classification import bucket_for, classify, get_members
from classify.dataclasses import Bucket, Member
from classify.hooks import NO_HOOKS, Hooks

from .dummy_class import DummyClass


def member_for(name, obj):
    def hook(cls):
        yield Member(name=name, kind="data", cls=cls, obj=obj)

    return hook


def test_bucket_hook_overrides_the_default():
    hooks = Hooks(buckets=[lambda _: Bucket.UNKNOWN])

    members = get_members(DummyClass)
    member = first(members, key=lambda m: m.name == "my_int")

    assert bucket_for(member) == Bucket.ATTRIBUTE
    assert bucket_for(member, hooks) == Bucket.UNKNOWN


def test_bucket_hook_can_defer():
    hooks = Hooks(buckets=[lambda _: None, lambda _: Bucket.NATIVE])

    members = get_members(DummyClass)
    member = first(members, key=lambda m: m.name == "my_int")

    assert bucket_for(member, hooks) == Bucket.NATIVE


def test_classify_passes_hooks_to_inner_classes():
    data = classify(
        DummyClass,
        hooks=Hooks(members=[member_for("invisible", "added")]),
    )

    assert "invisible" in data.attributes

    meta = first(data.classes, key=lambda c: c.name == "Meta")
    assert "invisible" in meta.attributes


def test_get_members_with_no_hooks_is_unchanged():
    assert get_members(DummyClass, NO_HOOKS) == get_members(DummyClass)


def test_hooks_defaults_to_nothing():
    assert Hooks() == NO_HOOKS
    assert NO_HOOKS.members == ()
    assert NO_HOOKS.buckets == ()


def test_hooks_or_combines_in_order():
    def first(cls): ...

    def second(cls): ...

    def bucket(member): ...

    combined = Hooks(members=[first]) | Hooks(members=[second], buckets=[bucket])

    assert combined.members == (first, second)
    assert combined.buckets == (bucket,)


def test_hooks_rejects_a_non_iterable_hook():
    # check the common missing trailing comma is caught
    def hook(cls): ...

    with pytest.raises(TypeError):
        Hooks(members=hook)  # ty: ignore[invalid-argument-type]


def test_hooks_stores_any_sequence_as_a_tuple():
    def hook(cls): ...

    hooks = Hooks(
        members=[hook],  # list
        buckets=(h for h in []),  # generator
    )

    assert hooks.members == (hook,)
    assert hooks.buckets == ()


def test_last_hook_is_the_winner():
    hooks = Hooks(
        members=[
            member_for("invisible", "first"),
            member_for("invisible", "second"),
        ]
    )

    members = get_members(DummyClass, hooks)

    invisible = first(members, key=lambda m: m.name == "invisible")
    assert invisible.obj == "second"


def test_member_hook_adds_a_member():
    assert "invisible" not in {m.name for m in get_members(DummyClass)}

    members = get_members(
        DummyClass,
        Hooks(members=[member_for("invisible", "added")]),
    )

    invisible = first(members, key=lambda m: m.name == "invisible")
    assert invisible.obj == "added"


def test_member_hook_overrides_an_existing_member():
    # the original is a method, so overriding it also changes its bucket
    members = get_members(DummyClass)
    member = first(members, key=lambda m: m.name == "one")
    assert bucket_for(member) == Bucket.METHOD

    members = get_members(
        DummyClass,
        Hooks(members=[member_for("one", "replaced")]),
    )
    one = first(members, key=lambda m: m.name == "one")
    assert one == Member(name="one", kind="data", cls=DummyClass, obj="replaced")
    assert bucket_for(one) == Bucket.ATTRIBUTE
