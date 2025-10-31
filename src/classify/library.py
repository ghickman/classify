import builtins
import collections
import inspect
import pydoc
import sys
from collections.abc import Generator
from typing import TypeVar

from attrs import Factory, frozen

from .exceptions import NotAClassError


C = TypeVar("C")


@frozen
class Attribute:
    name: str
    object: str
    defining_class: str
    value: str


@frozen
class Class:
    name: str
    docstring: str
    ancestors: list[str]
    parents: list[str]
    attributes: dict[str, list[Attribute]]
    methods: dict[str, list["Method"]]
    properties: list = Factory(list)


@frozen
class Line:
    start: int
    total: int


@frozen
class Method:
    name: str
    docstring: str
    defining_class: str
    arguments: str
    code: str
    lines: Line
    file: str | None = None


def get_members(obj):
    """
    Get members from the given object

    classify_class_attrs returns a tuple of:
     - name
     - kind
     - class
     - object
    """
    members = pydoc.classify_class_attrs(obj)
    # filter down to non-private items and those defined on the given object
    return [
        member
        for member in members
        if pydoc.visiblename(member[0], obj=obj) and member[2] == obj
    ]


def classify[C](obj: type[C]) -> Class:
    # flatten the MRO of the given class and flip the order so it's the first
    # non-object class first
    mro = [cls for cls in reversed(inspect.getmro(obj)) if cls is not builtins.object]

    # build up dicts of attrs&methods, by name, because they can be defined on
    # more than one class in the MRO
    attributes = collections.defaultdict(list)
    methods = collections.defaultdict(list)

    for cls in mro:
        members = list(get_members(cls))

        ## ATTRIBUTES
        class_attrs = [m for m in members if m[1] == "data"]
        for attribute in build_attributes(class_attrs, obj):
            attributes[attribute.name].append(attribute)

        ## METHODS
        instance_methods = [
            m for m in members if m[1] in ["method", "class method", "static method"]
        ]
        for method in build_methods(instance_methods):
            methods[method.name].append(method)

    return Class(
        name=obj.__name__,
        docstring=pydoc.getdoc(obj),
        ancestors=[k.__name__ for k in mro],
        parents=inspect.getclasstree([obj])[-1][0][1],
        attributes=dict(sorted(attributes.items())),
        methods=dict(sorted(methods.items())),
    )


def build_attributes(attributes, obj) -> Generator[Attribute, None, None]:
    """Build the Attribute list for the given object."""
    for attr in attributes:
        obj = getattr(attr[2], attr[0])

        yield Attribute(
            name=attr[0],
            object=obj,
            defining_class=attr[2].__name__,
            value=str(obj),
        )


def build_methods(methods) -> Generator[Method, None, None]:
    for method in methods:
        func = getattr(method[2], method[0])

        arguments = str(inspect.signature(func))

        # Get source line details
        lines, start_line = inspect.getsourcelines(func)

        yield Method(
            name=method[0],
            docstring=pydoc.getdoc(method[3]),
            defining_class=method[2],
            arguments=arguments,
            code="".join(lines),
            lines=Line(start=start_line, total=len(lines)),
            file=inspect.getsourcefile(func),
        )


def resolve(thing: str) -> type[C]:
    """Find the given thing and ensure it's a class"""
    sys.path.insert(0, "")

    obj, _ = pydoc.resolve(thing)  # ty: ignore[not-iterable]

    if not inspect.isclass(obj):
        raise NotAClassError

    return obj
