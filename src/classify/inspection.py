import inspect


def is_function(obj) -> bool:
    """
    Can we treat the given object as a function?

    inspect gives us a lot of things which quack like functions, even when we
    can't get a signature or source for them.  So, check we have a Python
    function once any wrappers have been removed.
    """
    return inspect.isfunction(unwrap(obj))


def unwrap(obj):
    """
    Get the function underneath any wrapper structure

    Method members can arrive with various types of wrapping, eg decorators,
    partials, cached properties, etc.  The wrapper object keeps a reference the
    wrapped object, and this function walks that path until it finds the actual
    object at the bottom.
    """
    seen = set()
    while id(obj) not in seen:
        seen.add(id(obj))

        for attribute in ("func", "__func__", "__wrapped__"):
            wrapped = getattr(obj, attribute, None)
            if wrapped is not None:
                obj = wrapped
                break

    return obj
