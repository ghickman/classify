import inspect
import pydoc
from typing import Any, Literal, Self

import structlog
from attrs import frozen


logger = structlog.get_logger()

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
        getter = Method.from_func(member.obj.fget, member.cls)
        setter = Method.from_func(member.obj.fset, member.cls)
        deleter = Method.from_func(member.obj.fdel, member.cls)

        return cls(name=member.name, getter=getter, setter=setter, deleter=deleter)


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
    defining_class: "SimpleClass"
    arguments: str
    code: str
    lines: Line
    file: str | None = None

    @classmethod
    def from_func(cls, func, defining_class) -> Self:
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
            name=func.__name__,
            docstring=pydoc.getdoc(func),
            defining_class=SimpleClass.from_class(defining_class),
            arguments=arguments,
            code="".join(lines),
            lines=Line(start=start_line, total=len(lines)),
            file=file,
        )

    @classmethod
    def from_member(cls, member: "Member") -> Self:
        logger.debug("extracting method")
        return cls.from_func(member.obj, member.cls)


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
