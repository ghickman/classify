import inspect
import pydoc
from typing import Any, Literal, Self

import structlog
from attrs import frozen

from .inspection import unwrap


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
class Line:
    source: str
    start: int
    total: int

    @classmethod
    def from_obj(cls, obj) -> Self | None:
        """
        Get source line details from the given object

        Dynamically created objects have no source for us to get lines from so
        this can fail, hence the optional None return.
        """
        try:
            source, start_line = inspect.getsourcelines(obj)
        except (OSError, TypeError):
            logger.debug("could not find source for class", cls=obj)
            return None

        return Line(source=source, start=start_line, total=len(source))


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
    ancestors: list["SimpleClass"]
    parents: list[type]
    attributes: dict[str, list[Attribute]]
    classes: list["Class"]
    properties: dict[str, list["Method"]]
    data_descriptors: dict[str, list["DataDescriptor"]]
    methods: dict[str, list["Method"]]
    lines: Line | None


@frozen
class DataDescriptor:
    name: str
    getter: "Method | None"
    setter: "Method | None"
    deleter: "Method | None"

    @classmethod
    def from_member(cls, member: "Member") -> Self:
        logger.debug("extracting data descriptor")

        getter = None
        if fget := getattr(member.obj, "fget", None):
            getter = Method.from_func(fget, member.cls)

        setter = None
        if fset := getattr(member.obj, "fset", None):
            setter = Method.from_func(fset, member.cls)

        # property() creates an fdel with the value `None`
        deleter = None
        if fdel := getattr(member.obj, "fdel", None):
            deleter = Method.from_func(fdel, member.cls)

        return cls(name=member.name, getter=getter, setter=setter, deleter=deleter)


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
        func = unwrap(func)

        arguments = str(inspect.signature(func))

        # Get source line details
        lines = Line.from_obj(func)
        code = "".join(lines.source) if lines else ""

        file = inspect.getsourcefile(func)

        return cls(
            name=func.__name__,
            docstring=pydoc.getdoc(func),
            defining_class=SimpleClass.from_class(defining_class),
            arguments=arguments,
            code=code,
            lines=lines,
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
