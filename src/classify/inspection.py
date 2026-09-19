import structlog


logger = structlog.get_logger()


def safe_getattr(obj, attribute, default=None):
    """
    getattr(), but treats any failure as a missing attribute

    Python being a dynamic language brings some challenges for introspection.
    In this case, a __getattr__ that does not behave as expected can cause fun
    and interesting problems when trying to get the original definition.  We
    could use inspect.getattr_static but that stops us being able to uwrap
    descriptors, breaking lots of definitions.
    """
    try:
        return getattr(obj, attribute, default)
    except Exception:  # noqa: BLE001
        logger.debug("getattr failed, using default", obj=obj, attribute=attribute)
        return default


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
            wrapped = safe_getattr(obj, attribute)
            if wrapped is not None:
                obj = wrapped
                break

    return obj
