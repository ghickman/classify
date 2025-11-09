import functools

from django.utils.decorators import classonlymethod
from django.utils.functional import cached_property


def my_decorator(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        f(*args, **kwargs)

    return wrapper


class DummyParent:
    def one(self):
        print("one parent")

    def three(self):
        pass


class DummyClass(DummyParent):
    """The main testing class"""

    some_attribute = 7

    def __init__(self):
        super().__init__()

    def _internal(self):
        pass

    def one(self):
        super().one()
        print("one child")

    def two(self):
        pass

    @my_decorator
    def four(self):
        pass

    # TODO: support rendering properties as methods
    @property
    def my_property(self):
        pass

    @functools.cached_property
    def my_cached_prop(self):
        pass

    @cached_property
    def my_dj_cached_prop(self):
        pass

    @classmethod
    def class_method(cls):
        pass

    @classonlymethod
    def class_only_method(self):
        pass

    @staticmethod
    def static_method():
        pass
