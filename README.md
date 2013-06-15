Classy
======

Generate concrete Class documentation for python Classes.

Usage:

    classy <python.path.to.Class>
    classy django.views.generic.DetailView
    classy django.forms.ModelForm
    classy extra_views.formsets.InlineFormSetView
    classy requests.sessions.Session


TODO:
* `--serve` spins up a `SimpleHTTPServer` on 8000 and opens with `webbrowser`
* `--port` as an extra option to `--server` to set the port
* Abstract front end bits away and move rest into `libclassy`
