import inspect

from .dataclasses import Member
from .inspection import is_function


def is_attribute(member: Member) -> bool:
    return member.kind == "data" and not is_inner_class(member)


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

    stdlib's inspect treats all non-data descriptors as methods.  This captures
    any members not defined in C, but also dynamically created ones, eg
    Django's DeferredAttribute.  We can't get the source for any of these
    members so also filter down to anything with an underlying function.
    """
    return member.kind in [
        "method",
        "class method",
        "static method",
    ] and is_function(member.obj)


def is_property(member: Member) -> bool:
    return member.kind == "readonly property"
