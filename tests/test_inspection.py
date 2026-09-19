from first import first

from classify.classification import bucket_for, get_members
from classify.dataclasses import Bucket
from classify.inspection import safe_getattr, unwrap


class RaisingMeta(type):
    """
    A metaclass which makes its classes non-data descriptors

    Mirror urlman's UrlsMetaclass where accessing an attribute on the class
    returns an instance of the class itself:

    https://github.com/andrewgodwin/urlman/blob/2.0.3/urlman/__init__.py#L53
    """

    def __get__(cls, instance, owner):
        return cls(instance, owner)


class Raising(metaclass=RaisingMeta):
    """An object with a __getattr__ that raises something other than AttributeError"""

    def __init__(self, instance=None, owner=None):
        self.instance = instance
        # urlman correctly sets these so stdlib introspection can get far
        # enough to reach the attributes we probe for
        self.__objclass__ = owner
        self.__qualname__ = type(self).__qualname__
        self.__name__ = type(self).__name__

    def __getattr__(self, attribute):
        msg = f"No attribute called {attribute!r}"
        raise ValueError(msg)


def test_bucket_for_descriptor_with_raising_getattr():
    class DummyClass:
        nested = Raising

    members = get_members(DummyClass)
    member = first(members, key=lambda m: m.name == "nested")

    assert bucket_for(member) == Bucket.NATIVE


def test_safe_getattr_with_existing_attribute():
    assert safe_getattr(Raising(), "instance", "default") is None


def test_safe_getattr_with_raising_getattr():
    assert safe_getattr(Raising(), "missing", "default") == "default"


def test_unwrap_with_raising_getattr():
    obj = Raising()

    assert unwrap(obj) is obj
