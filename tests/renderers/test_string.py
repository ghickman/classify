from classify.renderers.string import docstring


def test_docstring():
    assert docstring("") == ""
