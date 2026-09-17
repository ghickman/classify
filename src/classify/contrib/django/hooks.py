from collections.abc import Iterable
from typing import Any

import structlog
from attrs import frozen
from django.db.migrations.writer import MigrationWriter

from classify.dataclasses import Member
from classify.hooks import Hooks


logger = structlog.get_logger()


@frozen
class FieldDefinition:
    """
    A field and the source that defined it

    A field's repr doesn't tell us very much about it, eg "my_field" just
    returns `my_app.MyModel.my_field`.  This class is a simple wrapper to hold
    both the object itself and the definition we've built.  It's string repr
    returns the definition so that it behaves like other classes during
    rendering.
    """

    field: Any
    definition: str

    def __str__(self) -> str:
        return self.definition


def definition_for(field) -> FieldDefinition:
    """
    Render the source of the given field

    Since Django is already doing this for migrations, we're making use of that.
    """
    try:
        definition, _ = MigrationWriter.serialize(field)
    except (AttributeError, ValueError):
        # just in case deconstruct() isn't working as expected
        logger.debug("could not build a definition for field", field=field)
        definition = f"{path_for(field)}(...)"

    return FieldDefinition(field=field, definition=definition)


def form_fields(cls) -> Iterable[Member]:
    """
    Expose the fields of a Django form

    Django's DeclarativeFieldsMetaclass takes each field from the class and
    moves it into declared_fields.
    """
    declared = vars(cls).get("declared_fields")
    if declared is None:
        return

    for name, field in declared.items():
        # filter out any inherited fields
        if any(name in getattr(base, "declared_fields", {}) for base in cls.__bases__):
            continue

        # no deconstruct() for form fields so we can't get a definitive definition
        definition = FieldDefinition(field=field, definition=f"{path_for(field)}(...)")

        yield Member(name=name, kind="data", cls=cls, obj=definition)


def model_fields(cls) -> Iterable[Member]:
    """
    Expose the fields of a Django model

    Django's ModelBase takes each field from the class body and replaces it
    with a descriptor, eg DeferredAttribute, placing the original field into
    _meta.  This hook reconstructs those fields for classify to consume.
    """
    # get _meta for this class, and this class only.  Asking for it via
    # cls.__dict__ avoids grabbing an inherited one.
    meta = vars(cls).get("_meta")
    if meta is None:
        return

    # use the local_ prefix to find fields declared on the current class, to
    # match how we filter members to their defining class in core
    for field in [*meta.local_fields, *meta.local_many_to_many]:
        yield Member(name=field.name, kind="data", cls=cls, obj=definition_for(field))


def path_for(obj) -> str:
    """The dotted path to the given object's class, tries to match Django's own shortening"""
    cls = type(obj)

    module = cls.__module__
    for package, alias in [("django.db.models", "models"), ("django.forms", "forms")]:
        if module.startswith(package):
            return f"{alias}.{cls.__qualname__}"

    return f"{module}.{cls.__qualname__}"


hooks = Hooks(members=[model_fields, form_fields])
