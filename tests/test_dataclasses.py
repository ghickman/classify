import functools

from classify.dataclasses import Method


def test_cached_properties():
    class DummyClass:
        @functools.cached_property
        def cached_prop(self): ...

    method = Method.from_func(DummyClass.cached_prop, DummyClass)

    # check that we get the method, and not the decorator
    assert method.name == "cached_prop"
