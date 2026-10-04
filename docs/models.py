from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    published = models.DateTimeField(null=True)

    class Meta:
        app_label = "docs"

    def __str__(self):
        return self.title
