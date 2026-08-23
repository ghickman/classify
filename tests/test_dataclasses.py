import functools

from classify.dataclasses import DataDescriptor, Member, Method


def test_cached_properties():
    class DummyClass:
        @functools.cached_property
        def cached_prop(self): ...

    method = Method.from_func(DummyClass.cached_prop, DummyClass)

    # check that we get the method, and not the decorator
    assert method.name == "cached_prop"


def test_data_descriptors_without_getter():
    class DummyClass:
        def set_value(self, value): ...

        value = property(None, set_value)

    member = Member(
        name="value", kind="data descriptor", cls=DummyClass, obj=DummyClass.value
    )

    descriptor = DataDescriptor.from_member(member)

    assert descriptor.getter is None
    assert descriptor.setter.name == "set_value"
    assert descriptor.deleter is None
