import pytest

from classify.classification import classify
from classify.resolution import resolve


pytestmark = pytest.mark.usefixtures("setup_dj")


def test_form():
    from tests.django_proj.core.models import DummyForm  # noqa: PLC0415

    data = classify(DummyForm)

    assert data.name == "DummyForm"
    breakpoint()
    assert "name" in data.attributes


def test_model():
    from tests.django_proj.core.models import DummyModel  # noqa: PLC0415

    data = classify(DummyModel)

    assert data.name == "DummyModel"
    assert "name" in data.attributes


def test_views():
    data = classify(resolve("django.views.generic.CreateView"))
    assert data.name == "CreateView"
    assert len(data.ancestors) == 9  # noqa: PLR2004
    assert "form_class" in data.attributes

    data = classify(resolve("django.views.generic.UpdateView"))
    assert data.name == "UpdateView"
    assert len(data.ancestors) == 9  # noqa: PLR2004
    assert "queryset" in data.attributes
