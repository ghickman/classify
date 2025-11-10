import builtins
import collections
import inspect
import pydoc
import sys
from collections.abc import Generator
from typing import Any, Literal, TypeVar

from attrs import Factory, frozen

from .exceptions import NotAClassError


C = TypeVar("C")
Kind = Literal[
    "class method",
    "static method",
    "property",
    "method",
    "data",
    "data descriptor",
    "readonly property",
]


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
class Member[C]:
    name: str
    kind: Kind
    cls: type[C]
    obj: Any


@frozen
class Method:
    name: str
    docstring: str
    defining_class: str
    arguments: str
    code: str
    lines: Line
    file: str | None = None


def build_attributes(members: list[Member]) -> Generator[Attribute, None, None]:
    """Build the Attribute list for the given Members"""
    for member in members:
        yield Attribute(
            name=member.name,
            object=member.obj,
            defining_class=member.cls.__name__,
            value=str(member.obj),
        )


def build_methods(members: list[Member]) -> Generator[Method, None, None]:
    """Build the Method list for the given Members"""
    for member in members:
        func = member.obj

        # get target of cached property decorators
        if hasattr(func, "func"):
            while getattr(func, "func", None):
                func = func.func

        # unwrap decorated methods and functions
        if hasattr(func, "__wrapped__"):  # decorated methods
            while getattr(func, "__wrapped__", None):
                func = func.__wrapped__

        arguments = str(inspect.signature(func))

        # Get source line details
        lines, start_line = inspect.getsourcelines(func)

        yield Method(
            name=member.name,
            docstring=pydoc.getdoc(member.obj),
            defining_class=member.cls,
            arguments=arguments,
            code="".join(lines),
            lines=Line(start=start_line, total=len(lines)),
            file=inspect.getsourcefile(func),
        )


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
        class_attrs = [m for m in members if m.kind == "data"]
        for attribute in build_attributes(class_attrs):
            attributes[attribute.name].append(attribute)

        ## METHODS
        instance_methods = [
            m for m in members if m.kind in ["method", "class method", "static method"]
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


def get_members(obj) -> list[Member]:
    """
    Get members from the given object

    classify_class_attrs returns a tuple of:
     - name
     - kind
     - class
     - object
    """
    members = [
        Member(
            name=m[0],
            kind=m[1],
            cls=m[2],
            obj=m[3],
        )
        for m in pydoc.classify_class_attrs(obj)
    ]
    # filter down to non-private items and those defined on the given object
    return [
        member
        for member in members
        if pydoc.visiblename(member.name, obj=obj) and member.cls == obj
    ]


def resolve(thing: str) -> type[C]:
    """Find the given thing and ensure it's a class"""
    sys.path.insert(0, "")

    obj, _ = pydoc.resolve(thing)  # ty: ignore[not-iterable]

    if not inspect.isclass(obj):
        raise NotAClassError

    return obj
