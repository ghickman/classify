# Classify

![PyPI Version](https://img.shields.io/pypi/v/classify)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ghickman/classify/main.yml)
![Python Versions](https://img.shields.io/pypi/pyversions/classify)


See everything a Python class inherits, and the code behind it.

Classify walks a class's [MRO](https://docs.python.org/3/glossary.html#term-method-resolution-order), gathers every member it inherits (methods, attributes, properties, etc.), and displays the class as though it had been written in one place, source code included.

It outputs to the terminal or HTML, or you can use it as a library and do what you want with the results.

If you've used [CCBV](https://ccbv.co.uk), but wanted it for any Python class, then classify is here to help.


## Installation
Classify imports the classes you point it at, so it has to live alongside the code you want to look at.
Install it as a development dependency of the project you're inspecting, in the same virtual environment.

Beyond that it's an ordinary Python package, so however you usually install one will do, eg:

```bash
pip install classify
```

or

```bash
uv add --dev classify
```


## Examples
### Simple class hierarchy
Take this example:
<!--[[[cog
from docs.helpers import source

cog.out(source("docs/example.py"))
]]]-->
```python
class Greeter:
    def greet(self):
        return f"Hello, {self.name}"


class Person(Greeter):
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Croeso, {self.name}"
```
<!--[[[end]]]-->

pass it to classify via its dotted path:
```bash
classify dotted.path.to.Person
```

and it shows you everything `Person` has defined on it.

Overridden methods are included, earliest in the inheritance tree first, with a comment to say which class they were defined on.

<!--[[[cog
from docs.helpers import cli

cog.out(cli("classify", "docs.example.Person", language="python"))
]]]-->
```python
class Person(Greeter):

    def __init__(self, name):
        self.name = name

    # Defined on: Greeter
    def greet(self):
        return f"Hello, {self.name}"

    def greet(self):
        return f"Croeso, {self.name}"
```
<!--[[[end]]]-->

Curious how it works with a larger class?  Try it out with the standard library's `http.server.SimpleHTTPRequestHandler`, which has 3 parent classes in its inheritance tree:

```bash
classify http.server.SimpleHTTPRequestHandler
```

### Django
Django classes (models, forms, etc.) work too, as long as you give classify a settings module to bootstrap Django with.

Take a model:
<!--[[[cog
from docs.helpers import source

cog.out(source("docs/models.py"))
]]]-->
```python
from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    published = models.DateTimeField(null=True)

    class Meta:
        app_label = "docs"

    def __str__(self):
        return self.title
```
<!--[[[end]]]-->

and pass its dotted path along with `--django-settings`:
```bash
classify docs.models.Article --django-settings docs.settings
```

Fields are rendered as the source that declared them, using the same serialiser Django writes migrations with:
<!--[[[cog
from docs.helpers import members

cog.out(members("classify", "docs.models.Article", "--django-settings", "docs.settings"))
]]]-->
```python
class Article(Model):
    """
    Article(id, title, slug, published)
    """
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    objects = docs.Article.objects
    published = models.DateTimeField(null=True)
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)

    # ... 779 more lines
```
<!--[[[end]]]-->

Django is only imported when you pass `--django-settings`, so it doesn't need to be installed otherwise.


## Usage
<!--[[[cog
from docs.helpers import cli

cog.out(cli("classify", "--help", columns=80, language="bash"))
]]]-->
```bash
Usage: classify [OPTIONS] KLASS

  See everything a Python class inherits, and the code behind it.

Options:
  --console-theme TEXT            Theme to render console output with, any
                                  Pygments style works here  [default:
                                  monokai]
  --debug                         Show debug logs
  --django-settings TEXT          Pass a dotted path to your Django settings
                                  when using with a Django project.
                                  classify.contrib.django.settings exists if
                                  you need it.
  --renderer [console|html|pager]
                                  How would you like your content rendered?
                                  [default: console]
  -o, --output DIRECTORY          Path for output files to be saved
  -p, --port INTEGER              The port to serve content at, requires
                                  --serve  [default: 8000]
  -s, --serve                     Serve HTML content, requires --renderer=html
  --version                       Show the version and exit.
  --help                          Show this message and exit.
```
<!--[[[end]]]-->

`--console-theme` takes the name of any style Pygments ships with; they're listed at <https://pygments.org/styles/>.
