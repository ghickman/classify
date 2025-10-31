from django.db import models


class DummyModel(models.Model):
    name = models.TextField()

    class Meta:
        app_label = "core"

    def __str__(self):
        return self.name
