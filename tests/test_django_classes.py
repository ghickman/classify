import pytest
from django.db import models
from django.forms import fields
from first import first

from classify.classification import classify
from classify.contrib.django.hooks import definition_for, hooks, path_for
from classify.resolution import resolve


pytestmark = pytest.mark.usefixtures("setup_dj")


class BrokenField(models.TextField):
    def deconstruct(self):
        raise ValueError


def test_definition_for_undeconstructable_field():
    definition = definition_for(BrokenField())

    assert definition.definition == "tests.test_django_classes.BrokenField(...)"


def test_form():
    from tests.django_proj.core.models import DummyForm  # noqa: PLC0415

    data = classify(DummyForm, hooks=hooks)

    assert data.name == "DummyForm"
    assert "name" in data.attributes

    # the metaclass removes fields from the class, so make sure the hook is
    # populating this
    assert len(data.attributes["name"]) == 1
    name = first(data.attributes["name"])
    assert isinstance(name.value.field, fields.CharField)

    assert str(name.value) == "forms.CharField(...)"


def test_form_inheritance():
    from tests.django_proj.core.models import DummyChildForm  # noqa: PLC0415

    data = classify(DummyChildForm, hooks=hooks)

    assert len(data.attributes["age"]) == 1
    age = first(data.attributes["age"])
    assert age.defining_class.name == "DummyChildForm"

    # declared_fields carries the parent's fields too, so check name is only
    # listed for the class where we defined it
    assert len(data.attributes["name"]) == 1
    name = first(data.attributes["name"])
    assert name.defining_class.name == "DummyForm"


def test_model_form():
    from tests.django_proj.core.models import DummyModelForm  # noqa: PLC0415

    data = classify(DummyModelForm, hooks=hooks)

    assert data.name == "DummyModelForm"

    # the metaclass builds Meta.model's fields into base_fields rather than
    # declared_fields, so make sure the hook is populating this
    assert len(data.attributes["name"]) == 1
    name = first(data.attributes["name"])
    assert isinstance(name.value.field, fields.CharField)

    assert str(name.value) == "forms.CharField(...)  # from core.DummyModel.name"


def test_model_form_declared_fields():
    from tests.django_proj.core.models import DummyMixedModelForm  # noqa: PLC0415

    data = classify(DummyMixedModelForm, hooks=hooks)

    # generated fields point back at the model field they came from
    for field_name in ["code", "name"]:
        assert len(data.attributes[field_name]) == 1
        attribute = first(data.attributes[field_name])
        assert str(attribute.value).endswith(f"# from core.DummyModel.{field_name}")

    # base_fields carries declared fields too, so check form_fields is the one
    # listing them, without a model field to point at
    assert len(data.attributes["extra"]) == 1
    extra = first(data.attributes["extra"])
    assert str(extra.value) == "forms.IntegerField(...)"


def test_model_form_inheritance():
    from tests.django_proj.core.models import DummyChildModelForm  # noqa: PLC0415

    data = classify(DummyChildModelForm, hooks=hooks)

    assert len(data.attributes["age"]) == 1
    age = first(data.attributes["age"])
    assert age.defining_class.name == "DummyChildModelForm"

    # the child regenerates its parent's fields into its own base_fields, so
    # check name is only listed for the class whose Meta produced it
    assert len(data.attributes["name"]) == 1
    name = first(data.attributes["name"])
    assert name.defining_class.name == "DummyModelForm"


def test_model():
    from tests.django_proj.core.models import DummyModel  # noqa: PLC0415

    data = classify(DummyModel, hooks=hooks)

    assert data.name == "DummyModel"
    assert "name" in data.attributes

    # check we've got the field as an attribute, with details, that's not been
    # bucketed in native
    assert len(data.attributes["name"]) == 1
    name = first(data.attributes["name"])
    assert isinstance(name.value.field, models.TextField)
    assert "name" not in data.native


def test_model_field_definitions():
    from tests.django_proj.core.models import DummyModel  # noqa: PLC0415

    data = classify(DummyModel, hooks=hooks)

    # kwargs come back from deconstruct() sorted, not in source order
    assert len(data.attributes["code"]) == 1
    code = first(data.attributes["code"])
    assert str(code.value) == "models.CharField(max_length=16, null=True, unique=True)"

    assert len(data.attributes["name"]) == 1
    name = first(data.attributes["name"])
    assert str(name.value) == "models.TextField()"


def test_model_relations():
    from tests.django_proj.core.models import DummyRelatedModel  # noqa: PLC0415

    data = classify(DummyRelatedModel, hooks=hooks)

    assert len(data.attributes["dummy"]) == 1
    dummy = first(data.attributes["dummy"])
    assert isinstance(dummy.value.field, models.ForeignKey)
    assert str(dummy.value).startswith("models.ForeignKey(")
    assert "to='core.dummymodel'" in str(dummy.value)

    assert len(data.attributes["tags"]) == 1
    tags = first(data.attributes["tags"])
    assert isinstance(tags.value.field, models.ManyToManyField)

    # check a ForeignKey's concrete column hasn't also been captured
    assert "dummy_id" not in data.attributes


def test_model_without_hooks():
    from tests.django_proj.core.models import DummyModel  # noqa: PLC0415

    data = classify(DummyModel)

    # check fields aren't captured when we're not using hooks
    assert "name" not in data.attributes
    assert "name" in data.native


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        (models.TextField(), "models.TextField"),
        (fields.CharField(), "forms.CharField"),
        (BrokenField(), "tests.test_django_classes.BrokenField"),
    ],
    ids=["model", "form", "third-party"],
)
def test_path_for(field, expected):
    assert path_for(field) == expected


def test_views():
    data = classify(resolve("django.views.generic.CreateView"), hooks=hooks)
    assert data.name == "CreateView"
    assert len(data.ancestors) == 9  # noqa: PLR2004
    assert "form_class" in data.attributes

    data = classify(resolve("django.views.generic.UpdateView"), hooks=hooks)
    assert data.name == "UpdateView"
    assert len(data.ancestors) == 9  # noqa: PLR2004
    assert "queryset" in data.attributes
