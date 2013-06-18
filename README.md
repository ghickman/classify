Classify
========

Generate concrete Class documentation for python Classes.

Usage:

    classify <python.path.to.Class>
    classify django.views.generic.DetailView
    classify django.forms.ModelForm
    classify extra_views.formsets.InlineFormSetView
    classify requests.sessions.Session


TODO:
* Abstract front end bits away and move rest into `libpydoc`
* Add config support
* Let user choose output file path
* Let user choose output template
