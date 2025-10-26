from nox import options
from nox_uv import session


options.default_venv_backend = "uv"


@session(python=["3.12", "3.13", "3.14"])
def tests(session):
    session.install(".[dev]")

    session.run("just", "console", *session.posargs, external=True)
    session.run("just", "html", *session.posargs, external=True)
