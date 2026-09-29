# Classify
See everything a Python class inherits, and the code behind it.

Classify walks a class's MRO, gathers every member it inherits (methods, attributes, properties, etc), and displays the class as though it had all been written in one place, source code included.

It outputs to the terminal or HTML, or you can use it as a library and do what you want with the results.


## Installation
```bash
pip install classify
```

or

```bash
uv add --dev classify
```


## Example
Take a simple class hierarchy:
```python
class Parent:
    def method(self):
        print("parent")


class Child(Parent):
    def method(self):
        print("child")
```

pass it to classify via its dotted path:
```bash
classify dotted.path.to.Child
```

and it shows you everything `Child` has defined on it:
```bash
class Child(Parent):

    # Defined on: Parent
    def method(self):
        print("parent")

    def method(self):
        print("child")
```


## Usage
```bash
classify <path.to.Class>
```

This outputs the full class definition, including any members defined on parent classes or mixins.

You can change the theme to any [Pygments theme](https://pygments.org/styles/) with `--console-theme`.

Output to your shell's pager with `--renderer pager`, or to [ccbv style pages](https://ccbv.co.uk) with `--renderer html`.

By default HTML documents are saved to a temporary directory.
To change this specify a relative location with the `--output` option.
You can serve the output, regardless of where its written to with `--serve`, and change the port with `--port`.

```bash
classify <path.to.Class> --renderer html --output output --serve --port 8080
```


## Why?
[CCBV](https://ccbv.co.uk) has long been a part of my everyday toolkit for working with Django's generic class-based views.
It's a fantastic resource for quick reference, but it only covers Django's GCBVs.

Classify aims to provide this same level of utility for all your Python classes.
