import inspect
import types

from .dataclasses import Member


def is_attribute(member: Member) -> bool:
    return (
        member.kind == "data"
        and not is_inner_class(member)
        and not is_cached_property(member)
    )


def is_cached_property(member: Member) -> bool:
    # covers functools.cached_property and variations like
    # django.utils.functional.cached_property.
    # These are method descriptors wrapping a function, so they get
    # reported as "method", but the descriptor is not callable.
    cls = type(member.obj)
    # getattr_static: getattr() would call arbitrary __getattr__
    # implementations on member values
    func = inspect.getattr_static(member.obj, "func", None)
    return (
        hasattr(cls, "__get__")
        and not hasattr(cls, "__set__")
        and not callable(member.obj)
        and callable(func)
    )


def is_data_descriptor(member: Member) -> bool:
    return (
        member.kind == "data descriptor"
        and not inspect.isgetsetdescriptor(member.obj)
        and not inspect.ismemberdescriptor(member.obj)
    )


def is_inner_class(member: Member) -> bool:
    if not inspect.isclass(member.obj):
        return False

    # inner class' __qualname__ will reflect that of the class they are defined
    # on, eg the.module.MyClass.Inner.  This check uses member.cls to build up
    # a prefix that can be removed from member.obj's __qualname__.  If the
    # remainder matches member.name then we have an inner class.
    name = member.obj.__qualname__.removeprefix(f"{member.cls.__qualname__}.")
    return name == member.name and member.kind == "data"


def is_method(member: Member) -> bool:
    """
    Filter out method members

    Excludes methods wrapped with descriptors defined in C since we can't get
    the source for those.
    """
    return (
        member.kind
        in [
            "method",
            "class method",
            "static method",
        ]
        and not isinstance(
            member.obj,
            (
                types.ClassMethodDescriptorType,
                types.MethodDescriptorType,
                types.WrapperDescriptorType,
            ),
        )
        and not inspect.isgetsetdescriptor(member.obj)
        and not inspect.isbuiltin(member.obj)
    )


def is_property(member: Member) -> bool:
    return member.kind == "readonly property"
