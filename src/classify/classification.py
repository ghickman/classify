import builtins
import collections
import inspect
import pydoc
from collections.abc import Iterable

import structlog

from .dataclasses import (
    Attribute,
    Bucket,
    Class,
    DataDescriptor,
    Line,
    Member,
    Method,
    SimpleClass,
    Unclassified,
)
from .filters import is_function, is_inner_class, is_native_descriptor


logger = structlog.get_logger()


def bucket_for(member: Member) -> Bucket:  # noqa: PLR0911
    """
    Find the right Bucket for the given Member

    pydoc defines a kinds on each member, see Kind for the full list.  We
    refine those here into classify's version.

    They're called buckets here because we're making sure we assign every
    member to _something_.
    """
    match member.kind:
        case "data":
            if is_inner_class(member):
                return Bucket.CLASS

            return Bucket.ATTRIBUTE

        case "method" | "class method" | "static method":
            # stdlib's inspect treats all non-data descriptors as methods.
            # That captures members defined in C, as well as dynamically
            # created ones, eg Django's DeferredAttribute.  We can't get source
            # for either, so only treat members with an underlying function as
            # methods.
            if is_function(member.obj):
                return Bucket.METHOD

            return Bucket.NATIVE

        case "readonly property":
            return Bucket.PROPERTY

        case "data descriptor":
            if is_native_descriptor(member):
                return Bucket.NATIVE

            return Bucket.DATA_DESCRIPTOR

        case _:
            # pydoc doesn't currently produce a kind which gets here, so this
            # is really a bit of speculative future-proofing.
            return Bucket.UNKNOWN


def bucket_members(members: Iterable[Member]) -> dict[Bucket, list[Member]]:
    """Assign every member to a Bucket"""
    buckets: dict[Bucket, list[Member]] = {bucket: [] for bucket in Bucket}

    for member in members:
        buckets[bucket_for(member)].append(member)

    return buckets


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
    native = collections.defaultdict(list)
    properties = collections.defaultdict(list)
    unknown = collections.defaultdict(list)

    structlog.contextvars.clear_contextvars()
    for cls in mro:
        structlog.contextvars.bind_contextvars(**{"class": cls.__name__})
        members = bucket_members(get_members(cls))

        ## ATTRIBUTES
        for member in members[Bucket.ATTRIBUTE]:
            structlog.contextvars.bind_contextvars(member=member)
            attributes[member.name].append(Attribute.from_member(member))

        ## CLASSES
        classes.extend(classify(c.obj) for c in members[Bucket.CLASS])

        ## METHODS
        for member in members[Bucket.METHOD]:
            structlog.contextvars.bind_contextvars(member=member)
            methods[member.name].append(Method.from_member(member))

        ## PROPERTIES
        for member in members[Bucket.PROPERTY]:
            logger.debug("extracting property", member=member)
            prop = Method.from_func(member.obj.fget, member.cls)
            properties[member.name].append(prop)

        ## DATA DESCRIPTORS
        for member in members[Bucket.DATA_DESCRIPTOR]:
            structlog.contextvars.bind_contextvars(member=member)
            data_descriptors[member.name].append(DataDescriptor.from_member(member))

        ## NATIVE
        for member in members[Bucket.NATIVE]:
            logger.debug("member has no Python source", member=member)
            native[member.name].append(Unclassified.from_member(member))

        ## UNKNOWN
        for member in members[Bucket.UNKNOWN]:
            logger.warning("could not classify member", member=member)
            unknown[member.name].append(Unclassified.from_member(member))

    ancestors = [SimpleClass.from_class(c) for c in mro[:-1]]

    return Class(
        name=obj.__name__,
        module=obj.__module__,
        docstring=pydoc.getdoc(obj),
        ancestors=ancestors,
        parents=get_parents(obj),
        attributes=dict(sorted(attributes.items())),
        classes=sorted(classes, key=lambda c: c.name),
        properties=dict(sorted(properties.items())),
        data_descriptors=dict(sorted(data_descriptors.items())),
        methods=dict(sorted(methods.items())),
        native=dict(sorted(native.items())),
        unknown=dict(sorted(unknown.items())),
        lines=Line.from_obj(obj),
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
        Member(name=name, kind=kind, cls=cls, obj=obj)
        for name, kind, cls, obj in pydoc.classify_class_attrs(obj)
    ]
    # filter down to non-private items and those defined on the given object
    return [
        member
        for member in members
        if pydoc.visiblename(member.name, obj=obj) and member.cls == obj
    ]


def get_parents[C](obj: type[C]) -> list[type]:
    tree = inspect.getclasstree([obj])

    # getclasstree returns a list of tuples, containing a class, and tuple with
    # that classes parents.  We just want the parents for the given obj.
    raw_parents = tree[-1][0][1]

    return [c for c in raw_parents if c is not builtins.object]
