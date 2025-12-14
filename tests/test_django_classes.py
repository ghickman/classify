from classify.classification import classify
from classify.resolution import resolve


def test_form(setup_dj):
    from tests.django_proj.core.models import DummyForm  # noqa: PLC0415

    classify(DummyForm)


def test_model(setup_dj):
    from tests.django_proj.core.models import DummyModel  # noqa: PLC0415

    classify(DummyModel)


def test_views(setup_dj):
    classify(resolve("django.views.generic.CreateView"))
    classify(resolve("django.views.generic.UpdateView"))
