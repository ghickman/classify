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
    classify <path.to.Class> --renderer html --output output --port 8080
```


## Why?
[CCBV](https://ccbv.co.uk) has long been a part of my everyday toolkit for working with Django's generic class-based views.
It's a fantastic resource for quick reference, but it only covers Django's GCBVs.

Classify aims to provide this same level of utility for all your Python classes.


## An Example
```bash
    class CreateView(SingleObjectTemplateResponseMixin, BaseCreateView):
        """
        View for creating a new object, with a response rendered by a template.
        """
        content_type = None
        context_object_name = None
        extra_context = None
        fields = None
        form_class = None
        http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
        initial = {}
        model = None
        pk_url_kwarg = pk
        prefix = None
        query_pk_and_slug = False
        queryset = None
        response_class = <class 'django.template.response.TemplateResponse'>
        slug_field = slug
        slug_url_kwarg = slug
        success_url = None
        template_engine = None
        template_name = None
        template_name_field = None
        template_name_suffix = _form
        view_is_async = False

        def __init__(self, **kwargs):
            """
            Constructor. Called in the URLconf; can contain helpful extra
            keyword arguments, and other things.
            """
            # Go through keyword arguments, and either save their values to our
            # instance, or raise an error.
            for key, value in kwargs.items():
                setattr(self, key, value)

        @classonlymethod
        def as_view(cls, **initkwargs):
            """Main entry point for a request-response process."""
            for key in initkwargs:
                if key in cls.http_method_names:
                    raise TypeError(
                        "The method name %s is not accepted as a keyword argument "
                        "to %s()." % (key, cls.__name__)
                    )
                if not hasattr(cls, key):
                    raise TypeError(
                        "%s() received an invalid keyword %r. as_view "
                        "only accepts arguments that are already "
                        "attributes of the class." % (cls.__name__, key)
                    )

            def view(request, *args, **kwargs):
                self = cls(**initkwargs)
                self.setup(request, *args, **kwargs)
                if not hasattr(self, "request"):
                    raise AttributeError(
                        "%s instance has no 'request' attribute. Did you override "
                        "setup() and forget to call super()?" % cls.__name__
                    )
                return self.dispatch(request, *args, **kwargs)

            view.view_class = cls
            view.view_initkwargs = initkwargs

            # __name__ and __qualname__ are intentionally left unchanged as
            # view_class should be used to robustly determine the name of the view
            # instead.
            view.__doc__ = cls.__doc__
            view.__module__ = cls.__module__
            view.__annotations__ = cls.dispatch.__annotations__
            # Copy possible attributes set by decorators, e.g. @csrf_exempt, from
            # the dispatch method.
            view.__dict__.update(cls.dispatch.__dict__)

            # Mark the callback if the view class is async.
            if cls.view_is_async:
                markcoroutinefunction(view)

            return view

        def dispatch(self, request, *args, **kwargs):
            # Try to dispatch to the right method; if a method doesn't exist,
            # defer to the error handler. Also defer to the error handler if the
            # request method isn't on the approved list.
            if request.method.lower() in self.http_method_names:
                handler = getattr(
                    self, request.method.lower(), self.http_method_not_allowed
                )
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

        def form_invalid(self, form):
            """If the form is invalid, render the invalid form."""
            return self.render_to_response(self.get_context_data(form=form))

        def form_valid(self, form):
            """If the form is valid, redirect to the supplied URL."""
            return HttpResponseRedirect(self.get_success_url())

        def form_valid(self, form):
            """If the form is valid, save the associated model."""
            self.object = form.save()
            return super().form_valid(form)

        def get(self, request, *args, **kwargs):
            """Handle GET requests: instantiate a blank version of the form."""
            return self.render_to_response(self.get_context_data())

        def get(self, request, *args, **kwargs):
            self.object = None
            return super().get(request, *args, **kwargs)

        def get_context_data(self, **kwargs):
            kwargs.setdefault("view", self)
            if self.extra_context is not None:
                kwargs.update(self.extra_context)
            return kwargs

        def get_context_data(self, **kwargs):
            """Insert the single object into the context dict."""
            context = {}
            if self.object:
                context["object"] = self.object
                context_object_name = self.get_context_object_name(self.object)
                if context_object_name:
                    context[context_object_name] = self.object
            context.update(kwargs)
            return super().get_context_data(**context)

        def get_context_data(self, **kwargs):
            """Insert the form into the context dict."""
            if "form" not in kwargs:
                kwargs["form"] = self.get_form()
            return super().get_context_data(**kwargs)

        def get_context_object_name(self, obj):
            """Get the name to use for the object."""
            if self.context_object_name:
                return self.context_object_name
            elif isinstance(obj, models.Model):
                return obj._meta.model_name
            else:
                return None

        def get_form(self, form_class=None):
            """Return an instance of the form to be used in this view."""
            if form_class is None:
                form_class = self.get_form_class()
            return form_class(**self.get_form_kwargs())

        def get_form_class(self):
            """Return the form class to use."""
            return self.form_class

        def get_form_class(self):
            """Return the form class to use in this view."""
            if self.fields is not None and self.form_class:
                raise ImproperlyConfigured(
                    "Specifying both 'fields' and 'form_class' is not permitted."
                )
            if self.form_class:
                return self.form_class
            else:
                if self.model is not None:
                    # If a model has been explicitly provided, use it
                    model = self.model
                elif getattr(self, "object", None) is not None:
                    # If this view is operating on a single object, use
                    # the class of that object
                    model = self.object.__class__
                else:
                    # Try to get a queryset and extract the model class
                    # from that
                    model = self.get_queryset().model

                if self.fields is None:
                    raise ImproperlyConfigured(
                        "Using ModelFormMixin (base class of %s) without "
                        "the 'fields' attribute is prohibited." % self.__class__.__name__
                    )

                return model_forms.modelform_factory(model, fields=self.fields)

        def get_form_kwargs(self):
            """Return the keyword arguments for instantiating the form."""
            kwargs = {
                "initial": self.get_initial(),
                "prefix": self.get_prefix(),
            }

            if self.request.method in ("POST", "PUT"):
                kwargs.update(
                    {
                        "data": self.request.POST,
                        "files": self.request.FILES,
                    }
                )
            return kwargs

        def get_form_kwargs(self):
            """Return the keyword arguments for instantiating the form."""
            kwargs = super().get_form_kwargs()
            if hasattr(self, "object"):
                kwargs.update({"instance": self.object})
            return kwargs

        def get_initial(self):
            """Return the initial data to use for forms on this view."""
            return self.initial.copy()

        def get_object(self, queryset=None):
            """
            Return the object the view is displaying.

            Require `self.queryset` and a `pk` or `slug` argument in the URLconf.
            Subclasses can override this to return any object.
            """
            # Use a custom queryset if provided; this is required for subclasses
            # like DateDetailView
            if queryset is None:
                queryset = self.get_queryset()

            # Next, try looking up by primary key.
            pk = self.kwargs.get(self.pk_url_kwarg)
            slug = self.kwargs.get(self.slug_url_kwarg)
            if pk is not None:
                queryset = queryset.filter(pk=pk)

            # Next, try looking up by slug.
            if slug is not None and (pk is None or self.query_pk_and_slug):
                slug_field = self.get_slug_field()
                queryset = queryset.filter(**{slug_field: slug})

            # If none of those are defined, it's an error.
            if pk is None and slug is None:
                raise AttributeError(
                    "Generic detail view %s must be called with either an object "
                    "pk or a slug in the URLconf." % self.__class__.__name__
                )

            try:
                # Get the single item from the filtered queryset
                obj = queryset.get()
            except queryset.model.DoesNotExist:
                raise Http404(
                    _("No %(verbose_name)s found matching the query")
                    % {"verbose_name": queryset.model._meta.verbose_name}
                )
            return obj

        def get_prefix(self):
            """Return the prefix to use for forms."""
            return self.prefix

        def get_queryset(self):
            """
            Return the `QuerySet` that will be used to look up the object.

            This method is called by the default implementation of get_object() and
            may not be called if get_object() is overridden.
            """
            if self.queryset is None:
                if self.model:
                    return self.model._default_manager.all()
                else:
                    raise ImproperlyConfigured(
                        "%(cls)s is missing a QuerySet. Define "
                        "%(cls)s.model, %(cls)s.queryset, or override "
                        "%(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
                    )
            return self.queryset.all()

        def get_slug_field(self):
            """Get the name of a slug field to be used to look up by slug."""
            return self.slug_field

        def get_success_url(self):
            """Return the URL to redirect to after processing a valid form."""
            if not self.success_url:
                raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
            return str(self.success_url)  # success_url may be lazy

        def get_success_url(self):
            """Return the URL to redirect to after processing a valid form."""
            if self.success_url:
                url = self.success_url.format(**self.object.__dict__)
            else:
                try:
                    url = self.object.get_absolute_url()
                except AttributeError:
                    raise ImproperlyConfigured(
                        "No URL to redirect to.  Either provide a url or define"
                        " a get_absolute_url method on the Model."
                    )
            return url

        def get_template_names(self):
            """
            Return a list of template names to be used for the request. Must return
            a list. May not be called if render_to_response() is overridden.
            """
            if self.template_name is None:
                raise ImproperlyConfigured(
                    "TemplateResponseMixin requires either a definition of "
                    "'template_name' or an implementation of 'get_template_names()'"
                )
            else:
                return [self.template_name]

        def get_template_names(self):
            """
            Return a list of template names to be used for the request. May not be
            called if render_to_response() is overridden. Return a list containing
            ``template_name``, if set on the value. Otherwise, return a list
            containing:

            * the contents of the ``template_name_field`` field on the
              object instance that the view is operating upon (if available)
            * ``<app_label>/<model_name><template_name_suffix>.html``
            """
            try:
                names = super().get_template_names()
            except ImproperlyConfigured:
                # If template_name isn't specified, it's not a problem --
                # we just start with an empty list.
                names = []

                # If self.template_name_field is set, grab the value of the field
                # of that name from the object; this is the most specific template
                # name, if given.
                if self.object and self.template_name_field:
                    name = getattr(self.object, self.template_name_field, None)
                    if name:
                        names.insert(0, name)

                # The least-specific option is the default <app>/<model>_detail.html;
                # only use this if the object in question is a model.
                if isinstance(self.object, models.Model):
                    object_meta = self.object._meta
                    names.append(
                        "%s/%s%s.html"
                        % (
                            object_meta.app_label,
                            object_meta.model_name,
                            self.template_name_suffix,
                        )
                    )
                elif getattr(self, "model", None) is not None and issubclass(
                    self.model, models.Model
                ):
                    names.append(
                        "%s/%s%s.html"
                        % (
                            self.model._meta.app_label,
                            self.model._meta.model_name,
                            self.template_name_suffix,
                        )
                    )

                # If we still haven't managed to find any template names, we should
                # re-raise the ImproperlyConfigured to alert the user.
                if not names:
                    raise ImproperlyConfigured(
                        "SingleObjectTemplateResponseMixin requires a definition "
                        "of 'template_name', 'template_name_field', or 'model'; "
                        "or an implementation of 'get_template_names()'."
                    )

            return names

        def http_method_not_allowed(self, request, *args, **kwargs):
            response = HttpResponseNotAllowed(self._allowed_methods())
            log_response(
                "Method Not Allowed (%s): %s",
                request.method,
                request.path,
                response=response,
                request=request,
            )

            if self.view_is_async:

                async def func():
                    return response

                return func()
            else:
                return response

        def options(self, request, *args, **kwargs):
            """Handle responding to requests for the OPTIONS HTTP verb."""
            response = HttpResponse()
            response.headers["Allow"] = ", ".join(self._allowed_methods())
            response.headers["Content-Length"] = "0"

            if self.view_is_async:

                async def func():
                    return response

                return func()
            else:
                return response

        def post(self, request, *args, **kwargs):
            """
            Handle POST requests: instantiate a form instance with the passed
            POST variables and then check if it's valid.
            """
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

        def post(self, request, *args, **kwargs):
            self.object = None
            return super().post(request, *args, **kwargs)

        def put(self, *args, **kwargs):
            return self.post(*args, **kwargs)

        def render_to_response(self, context, **response_kwargs):
            """
            Return a response, using the `response_class` for this view, with a
            template rendered with the given context.

            Pass response_kwargs to the constructor of the response class.
            """
            response_kwargs.setdefault("content_type", self.content_type)
            return self.response_class(
                request=self.request,
                template=self.get_template_names(),
                context=context,
                using=self.template_engine,
                **response_kwargs,
            )

        def setup(self, request, *args, **kwargs):
            """Initialize attributes shared by all view methods."""
            if hasattr(self, "get") and not hasattr(self, "head"):
                self.head = self.get
            self.request = request
            self.args = args
            self.kwargs = kwargs
```
