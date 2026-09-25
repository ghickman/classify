import os


def setup_django(settings_path: str) -> None:
    """
    Bootstrap Django

    When running against code that touches Django we need to do some
    bootstrapping first.
    """
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_path

    import django  # noqa: PLC0415

    django.setup()
