import os


def setup_django(settings_path: str) -> None:
    """
    Bootstrap Django

    When running classify against a Django project, rather than Django itself we
    Django projects sometimes need
    """
    # default = "classify.contrib.django.settings"
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_path

    import django  # noqa: PLC0415

    django.setup()
