from django import forms
from django.db import models


class DummyForm(forms.Form):
    name = forms.CharField()


class DummyChildForm(DummyForm):
    age = forms.IntegerField()


class DummyModel(models.Model):
    code = models.CharField(max_length=16, unique=True, null=True)
    name = models.TextField()

    class Meta:
        app_label = "core"

    def __str__(self):
        return self.name


class DummyRelatedModel(models.Model):
    dummy = models.ForeignKey(DummyModel, on_delete=models.CASCADE)
    tags = models.ManyToManyField("self")

    class Meta:
        app_label = "core"

    def __str__(self):
        return str(self.dummy)
