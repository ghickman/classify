import builtins
import collections
import inspect
import pydoc

import structlog

from .dataclasses import Attribute, Class, DataDescriptor, Member, Method, SimpleClass
from .filters import (
    is_attribute,
    is_data_descriptor,
    is_inner_class,
    is_method,
    is_property,
)


logger = structlog.get_logger()


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
        class_attrs = [m for m in members if is_attribute(m)]
        for member in class_attrs:
            structlog.contextvars.bind_contextvars(member=member)
            attributes[member.name].append(Attribute.from_member(member))

        ## CLASSES
        inner_classes = [m for m in members if is_inner_class(m)]
        classes.extend(classify(c.obj) for c in inner_classes)

        ## METHODS
        instance_methods = [m for m in members if is_method(m)]
        for member in instance_methods:
            structlog.contextvars.bind_contextvars(member=member)
            methods[member.name].append(Method.from_member(member))

        ## PROPERTIES
        props = [m for m in members if is_property(m)]
        for member in props:
            logger.debug("extracting property", member=member)
            prop = Method.from_func(member.obj.fget, member.cls)
            properties[member.name].append(prop)

        ## DATA DESCRIPTORS
        descriptors = [m for m in members if is_data_descriptor(m)]
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
