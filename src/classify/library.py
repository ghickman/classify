import builtins
import collections
import inspect
import pydoc
import sys
from typing import Any, Literal, Self, TypeVar

import structlog
from attrs import frozen

from .exceptions import NotAClassError


logger = structlog.get_logger()


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
    defining_class: "SimpleClass"
    value: Any

    @classmethod
    def from_member(cls, member: "Member") -> Self:
        logger.debug("extracting attribute", member=member)
        return cls(
            name=member.name,
            defining_class=SimpleClass.from_class(member.cls),
            value=member.obj,
        )


@frozen
class Class:
    name: str
    module: str
    docstring: str
    ancestors: list[str]
    parents: list[str]
    attributes: dict[str, list[Attribute]]
    classes: list["Class"]
    properties: dict[str, list["Method"]]
    data_descriptors: dict[str, list["DataDescriptor"]]
    methods: dict[str, list["Method"]]


@frozen
class DataDescriptor:
    name: str
    getter: "Method | None"
    setter: "Method | None"
    deleter: "Method | None"

    @classmethod
    def from_member(cls, member: "Member") -> Self:
        logger.debug("extracting data descriptor")

        # properties are have fget, fset, and fdel objects that are themselves
        # methods, can I pass those methods to build methods?
        getter = Method.from_member(func_to_member(member.obj.fget, member.cls))
        setter = Method.from_member(func_to_member(member.obj.fset, member.cls))
        deleter = Method.from_member(func_to_member(member.obj.fdel, member.cls))

        return cls(name=member.name, getter=getter, setter=setter, deleter=deleter)


@frozen
class SimpleClass:
    name: str
    module: str

    @staticmethod
    def from_class(klass):
        return SimpleClass(
            name=klass.__name__,
            module=klass.__module__,
        )


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
    defining_class: SimpleClass
    arguments: str
    code: str
    lines: Line
    file: str | None = None

    @classmethod
    def from_member(cls, member: "Member") -> Self:
        logger.debug("extracting method")
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

        file = inspect.getsourcefile(func)

        return cls(
            name=member.name,
            docstring=pydoc.getdoc(member.obj),
            defining_class=SimpleClass.from_class(member.cls),
            arguments=arguments,
            code="".join(lines),
            lines=Line(start=start_line, total=len(lines)),
            file=file,
        )


def classify[C](obj: type[C]) -> Class:
    # flatten the MRO of the given class and flip the order so it's the first
    # non-object class first
    mro = [cls for cls in reversed(inspect.getmro(obj)) if cls is not builtins.object]

    # build up dicts of attrs&methods, by name, because they can be defined on
    # more than one class in the MRO
    attributes = collections.defaultdict(list)
    classes = []
    data_descriptors = collections.defaultdict(list)
    methods = collections.defaultdict(list)
    properties = collections.defaultdict(list)

    structlog.contextvars.clear_contextvars()
    for cls in mro:
        structlog.contextvars.bind_contextvars(**{"class": cls.__name__})
        members = list(get_members(cls))

        ## ATTRIBUTES
        class_attrs = [m for m in members if m.kind == "data" and not is_inner_class(m)]
        for member in class_attrs:
            structlog.contextvars.bind_contextvars(member=member)
            attributes[member.name].append(Attribute.from_member(member))

        ## CLASSES
        inner_classes = [m for m in members if m.kind == "data" and is_inner_class(m)]
        classes.extend(classify(c.obj) for c in inner_classes)

        ## METHODS
        instance_methods = [
            m for m in members if m.kind in ["method", "class method", "static method"]
        ]
        for member in instance_methods:
            structlog.contextvars.bind_contextvars(member=member)
            methods[member.name].append(Method.from_member(member))

        ## PROPERTIES
        props = [m for m in members if m.kind == "readonly property"]
        for member in props:
            logger.debug("extracting property", member=member)
            prop = Method.from_member(func_to_member(member.obj.fget, member.cls))
            properties[member.name].append(prop)

        ## DATA DESCRIPTORS
        descriptors = [
            m
            for m in members
            if m.kind == "data descriptor"
            and not inspect.isgetsetdescriptor(m.obj)
            and not inspect.ismemberdescriptor(m.obj)
        ]
        for member in descriptors:
            structlog.contextvars.bind_contextvars(member=member)
            data_descriptors[member.name].append(DataDescriptor.from_member(member))

    ancestors = [SimpleClass.from_class(c) for c in mro[:-1]]

    return Class(
        name=obj.__name__,
        module=obj.__module__,
        docstring=pydoc.getdoc(obj),
        ancestors=ancestors,
        parents=get_parents(obj),
        attributes=dict(sorted(attributes.items())),
        classes=sorted(classes),
        properties=dict(sorted(properties.items())),
        data_descriptors=dict(sorted(data_descriptors.items())),
        methods=dict(sorted(methods.items())),
    )


def func_to_member(f, cls) -> Member:
    return Member(
        name=f.__name__,
        kind="method",
        cls=cls,
        obj=f,
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


def get_parents[C](obj: type[C]) -> list[str]:
    tree = inspect.getclasstree([obj])

    # getclasstree returns a list of tuples, containing a class, and tuple with
    # that classes parents.  We just want the parents for the given obj.
    raw_parents = tree[-1][0][1]

    return [c for c in raw_parents if c is not builtins.object]


def is_inner_class(member: Member) -> bool:
    if not inspect.isclass(member.obj):
        return False

    # inner class' __qualname__ will reflect that of the class they are defined
    # on, eg the.module.MyClass.Inner.  This check uses member.cls to build up
    # a prefix that can be removed from member.obj's __qualname__.  If the
    # remainder matches member.name then we have an inner class.
    name = member.obj.__qualname__.removeprefix(f"{member.cls.__qualname__}.")
    return name == member.name


def resolve(thing: str) -> type[C]:
    """Find the given thing and ensure it's a class"""
    sys.path.insert(0, "")

    obj, _ = pydoc.resolve(thing)  # ty: ignore[not-iterable]

    if not inspect.isclass(obj):
        raise NotAClassError

    return obj
