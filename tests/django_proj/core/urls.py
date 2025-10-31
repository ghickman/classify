from typing import ClassVar

from django.urls import path
from django.views.generic import UpdateView

from .models import DummyModel


class DummyUpdate(UpdateView):
    fields: ClassVar[list[str]] = ["name"]
    model = DummyModel


urlpatterns = [
    path("", DummyUpdate.as_view()),
]
