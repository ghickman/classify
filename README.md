# Classify
Generate concrete class API documentation for python Classes

## Installation
```bash
    pip install classify
```


## Usage
```bash
    classify <path.to.Class>
```

This outputs the full class definition, including the methods defined on each parent class.

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
