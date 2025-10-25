import builtins
import collections
import inspect
import os
import pydoc
import sys


def _is_method(t):
    return t[1] == "method" or t[1] == "class method" or t[1] == "static method"


def classify(klass, obj, name=None):
    if not inspect.isclass(obj):
        prefix = name if name else "Input"
        msg = f"{prefix} doesn't look like a class, please specify the path to a class"
        raise TypeError(msg)

    mro = list(reversed(inspect.getmro(obj)))

    klass.update(
        {
            "name": obj.__name__,
            "docstring": pydoc.getdoc(obj),
            "ancestors": [k.__name__ for k in mro],
            "parents": inspect.getclasstree([obj])[-1][0][1],
        },
    )

    def get_attrs(obj):
        all_attrs = filter(
            lambda data: pydoc.visiblename(data[0], obj=obj),
            pydoc.classify_class_attrs(obj),
        )
        return filter(lambda data: data[2] == obj, all_attrs)

    for cls in mro:
        if cls is builtins.object:
            continue

        attrs = list(get_attrs(cls))

        ## ATTRIBUTES
        attributes = build_attributes(filter(lambda t: t[1] == "data", attrs), obj)
        for attribute in attributes:
            name = attribute.pop("name")
            klass["attributes"][name].append(attribute)

        ## METHODS
        for method in build_methods(filter(_is_method, attrs)):
            name = method.pop("name")
            klass["methods"][name].append(method)

    return klass


def build_attributes(attributes, obj):
    """Build the Attribute list for the given object."""
    for attr in attributes:
        yield {
            "name": attr[0],
            "object": getattr(attr[2], attr[0]),
            "defining_class": attr[2],
        }


def build_methods(methods):
    for method in methods:
        func = getattr(method[2], method[0])
        # Get the method arguments
        arguments = inspect.getfullargspec(func)

        # Get source line details
        lines, start_line = inspect.getsourcelines(func)

        yield {
            "name": method[0],
            "docstring": pydoc.getdoc(method[3]),
            "defining_class": method[2],
            "arguments": arguments,
            "code": "".join(lines),
            "lines": {"start": start_line, "total": len(lines)},
            "file": inspect.getsourcefile(func),
        }


def build(thing):
    """Build a dictionary mapping of a class."""
    if "django" in thing:
        os.environ["DJANGO_SETTINGS_MODULE"] = "classify.contrib.django.settings"

    sys.path.insert(0, "")

    klass = {
        "attributes": collections.defaultdict(list),
        "methods": collections.defaultdict(list),
        "properties": [],
        "ancestors": [],
        "parents": [],
    }

    obj, name = pydoc.resolve(thing)
    return classify(klass, obj, name)
