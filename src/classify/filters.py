import inspect

from .dataclasses import Member
from .inspection import unwrap


def is_cached_property(obj) -> bool:
    """
    Is the given object a cached property?

    Cached properties are non-data descriptors, so inspect sees them as
    methods.  However, unlike a "real" method, or a decorated one, the
    descriptor object itself is not callable, it only implements __get__.  This
    is what separates cached_property and third party equivalents from what we
    consider methods.
    """
    return inspect.ismethoddescriptor(obj) and not callable(obj)


def is_function(obj) -> bool:
    """
    Can we treat the given object as a function?

    inspect gives us a lot of things which quack like functions, even when we
    can't get a signature or source for them.  So, check we have a Python
    function once any wrappers have been removed.
    """
    return inspect.isfunction(unwrap(obj))


def is_inner_class(member: Member) -> bool:
    if not inspect.isclass(member.obj):
        return False

    # inner class' __qualname__ will reflect that of the class they are defined
    # on, eg the.module.MyClass.Inner.  This check uses member.cls to build up
    # a prefix that can be removed from member.obj's __qualname__.  If the
    # remainder matches member.name then we have an inner class.
    name = member.obj.__qualname__.removeprefix(f"{member.cls.__qualname__}.")
    return name == member.name


def is_native_descriptor(member: Member) -> bool:
    """
    Is this data descriptor implemented in C?

    getset and member descriptors, eg __dict__ and __weakref__, have no Python
    source for us to render.
    """
    return inspect.isgetsetdescriptor(member.obj) or inspect.ismemberdescriptor(
        member.obj
    )
