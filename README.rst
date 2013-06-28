Classify
========

Generate concrete class API documentation for python Classes.

Installation
------------

.. code-block:: bash

    $ pip install classify


Usage
-----

.. code-block:: bash

    $ classify <python.path.to.Class>

This outputs by default to your shell's pager. However you can also generate an
HTML document to get CCBV_ style pages and even serve that document.

By default HTML documents are saved to ``/path/to/current/dir/output``.
To change this specify a relative location with the ``--output`` option.

.. code-block:: bash

    $ classify <python.path.to.Class> --html [--output [--serve [--port]]]


Why?
----
CCBV_ has long been part of my everyday toolkit for
working with Django's class-based views, it's a fantastic resource for quick
reference. But it only covers Django's CBVs.

Classify aims to be CCBV for all your Python classes.

.. _CCBV: http://ccbv.co.uk


An Example
----------

.. code-block:: bash

    $ classify django.views.generic.CreateView

    class CreateView(SingleObjectTemplateResponseMixin, BaseCreateView):
        """
        View for creating a new object instance,
        with a response rendered by template.
        """
        content_type = None
        context_object_name = None
        form_class = None
        http_method_names = [u'get', u'post', u'put', u'delete', u'head', u'options', u'trace']
        initial = {}
        model = None
        pk_url_kwarg = pk
        queryset = None
        response_class = <class 'django.template.response.TemplateResponse'>
        slug_field = slug
        slug_url_kwarg = slug
        success_url = None
        template_name = None
        template_name_field = None
        template_name_suffix = _form

        def __init__(self, **kwargs):
            """
            Constructor. Called in the URLconf; can contain helpful extra
            keyword arguments, and other things.
            """
            # Go through keyword arguments, and either save their values to our
            # instance, or raise an error.
            for key, value in six.iteritems(kwargs):
                setattr(self, key, value)

        @classonlymethod
        def as_view(cls, **initkwargs):
            """
            Main entry point for a request-response process.
            """
            # sanitize keyword arguments
            for key in initkwargs:
                if key in cls.http_method_names:
                    raise TypeError("You tried to pass in the %s method name as a "
                                    "keyword argument to %s(). Don't do that."
                                    % (key, cls.__name__))
                if not hasattr(cls, key):
                    raise TypeError("%s() received an invalid keyword %r. as_view "
                                    "only accepts arguments that are already "
                                    "attributes of the class." % (cls.__name__, key))

            def view(request, *args, **kwargs):
                self = cls(**initkwargs)
                if hasattr(self, 'get') and not hasattr(self, 'head'):
                    self.head = self.get
                self.request = request
                self.args = args
                self.kwargs = kwargs
                return self.dispatch(request, *args, **kwargs)

            # take name and docstring from class
            update_wrapper(view, cls, updated=())

            # and possible attributes set by decorators
            # like csrf_exempt from dispatch
            update_wrapper(view, cls.dispatch, assigned=())
            return view

        def dispatch(self, request, *args, **kwargs):
            # Try to dispatch to the right method; if a method doesn't exist,
            # defer to the error handler. Also defer to the error handler if the
            # request method isn't on the approved list.
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            return handler(request, *args, **kwargs)

        def form_invalid(self, form):
            """
            If the form is invalid, re-render the context data with the
            data-filled form and errors.
            """
            return self.render_to_response(self.get_context_data(form=form))

        def form_valid(self, form):
            """
            If the form is valid, redirect to the supplied URL.
            """
            return HttpResponseRedirect(self.get_success_url())

        def form_valid(self, form):
            """
            If the form is valid, save the associated model.
            """
            self.object = form.save()
            return super(ModelFormMixin, self).form_valid(form)

        def get(self, request, *args, **kwargs):
            """
            Handles GET requests and instantiates a blank version of the form.
            """
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            return self.render_to_response(self.get_context_data(form=form))

        def get(self, request, *args, **kwargs):
            self.object = None
            return super(BaseCreateView, self).get(request, *args, **kwargs)

        def get_context_data(self, **kwargs):
            if 'view' not in kwargs:
                kwargs['view'] = self
            return kwargs

        def get_context_data(self, **kwargs):
            """
            Insert the single object into the context dict.
            """
            context = {}
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
            context.update(kwargs)
            return super(SingleObjectMixin, self).get_context_data(**context)

        def get_context_data(self, **kwargs):
            """
            If an object has been supplied, inject it into the context with the
            supplied context_object_name name.
            """
            context = {}
            if self.object:
                context['object'] = self.object
                context_object_name = self.get_context_object_name(self.object)
                if context_object_name:
                    context[context_object_name] = self.object
            context.update(kwargs)
            return super(ModelFormMixin, self).get_context_data(**context)

        def get_context_object_name(self, obj):
            """
            Get the name to use for the object.
            """
            if self.context_object_name:
                return self.context_object_name
            elif isinstance(obj, models.Model):
                return obj._meta.object_name.lower()
            else:
                return None

        def get_form(self, form_class):
            """
            Returns an instance of the form to be used in this view.
            """
            return form_class(**self.get_form_kwargs())

        def get_form_class(self):
            """
            Returns the form class to use in this view
            """
            return self.form_class

        def get_form_class(self):
            """
            Returns the form class to use in this view.
            """
            if self.form_class:
                return self.form_class
            else:
                if self.model is not None:
                    # If a model has been explicitly provided, use it
                    model = self.model
                elif hasattr(self, 'object') and self.object is not None:
                    # If this view is operating on a single object, use
                    # the class of that object
                    model = self.object.__class__
                else:
                    # Try to get a queryset and extract the model class
                    # from that
                    model = self.get_queryset().model
                return model_forms.modelform_factory(model)

        def get_form_kwargs(self):
            """
            Returns the keyword arguments for instantiating the form.
            """
            kwargs = {'initial': self.get_initial()}
            if self.request.method in ('POST', 'PUT'):
                kwargs.update({
                    'data': self.request.POST,
                    'files': self.request.FILES,
                })
            return kwargs

        def get_form_kwargs(self):
            """
            Returns the keyword arguments for instantiating the form.
            """
            kwargs = super(ModelFormMixin, self).get_form_kwargs()
            kwargs.update({'instance': self.object})
            return kwargs

        def get_initial(self):
            """
            Returns the initial data to use for forms on this view.
            """
            return self.initial.copy()

        def get_object(self, queryset=None):
            """
            Returns the object the view is displaying.

            By default this requires `self.queryset` and a `pk` or `slug` argument
            in the URLconf, but subclasses can override this to return any object.
            """
            # Use a custom queryset if provided; this is required for subclasses
            # like DateDetailView
            if queryset is None:
                queryset = self.get_queryset()

            # Next, try looking up by primary key.
            pk = self.kwargs.get(self.pk_url_kwarg, None)
            slug = self.kwargs.get(self.slug_url_kwarg, None)
            if pk is not None:
                queryset = queryset.filter(pk=pk)

            # Next, try looking up by slug.
            elif slug is not None:
                slug_field = self.get_slug_field()
                queryset = queryset.filter(**{slug_field: slug})

            # If none of those are defined, it's an error.
            else:
                raise AttributeError("Generic detail view %s must be called with "
                                     "either an object pk or a slug."
                                     % self.__class__.__name__)

            try:
                # Get the single item from the filtered queryset
                obj = queryset.get()
            except ObjectDoesNotExist:
                raise Http404(_("No %(verbose_name)s found matching the query") %
                              {'verbose_name': queryset.model._meta.verbose_name})
            return obj

        def get_queryset(self):
            """
            Get the queryset to look an object up against. May not be called if
            `get_object` is overridden.
            """
            if self.queryset is None:
                if self.model:
                    return self.model._default_manager.all()
                else:
                    raise ImproperlyConfigured("%(cls)s is missing a queryset. Define "
                                               "%(cls)s.model, %(cls)s.queryset, or override "
                                               "%(cls)s.get_queryset()." % {
                                                    'cls': self.__class__.__name__
                                            })
            return self.queryset._clone()

        def get_slug_field(self):
            """
            Get the name of a slug field to be used to look up by slug.
            """
            return self.slug_field

        def get_success_url(self):
            """
            Returns the supplied success URL.
            """
            if self.success_url:
                # Forcing possible reverse_lazy evaluation
                url = force_text(self.success_url)
            else:
                raise ImproperlyConfigured(
                    "No URL to redirect to. Provide a success_url.")
            return url

        def get_success_url(self):
            """
            Returns the supplied URL.
            """
            if self.success_url:
                url = self.success_url % self.object.__dict__
            else:
                try:
                    url = self.object.get_absolute_url()
                except AttributeError:
                    raise ImproperlyConfigured(
                        "No URL to redirect to.  Either provide a url or define"
                        " a get_absolute_url method on the Model.")
            return url

        def get_template_names(self):
            """
            Returns a list of template names to be used for the request. Must return
            a list. May not be called if render_to_response is overridden.
            """
            if self.template_name is None:
                raise ImproperlyConfigured(
                    "TemplateResponseMixin requires either a definition of "
                    "'template_name' or an implementation of 'get_template_names()'")
            else:
                return [self.template_name]

        def get_template_names(self):
            """
            Return a list of template names to be used for the request. May not be
            called if render_to_response is overridden. Returns the following list:

            * the value of ``template_name`` on the view (if provided)
            * the contents of the ``template_name_field`` field on the
              object instance that the view is operating upon (if available)
            * ``<app_label>/<object_name><template_name_suffix>.html``
            """
            try:
                names = super(SingleObjectTemplateResponseMixin, self).get_template_names()
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
                names.append("%s/%s%s.html" % (
                    self.object._meta.app_label,
                    self.object._meta.object_name.lower(),
                    self.template_name_suffix
                ))
            elif hasattr(self, 'model') and self.model is not None and issubclass(self.model, models.Model):
                names.append("%s/%s%s.html" % (
                    self.model._meta.app_label,
                    self.model._meta.object_name.lower(),
                    self.template_name_suffix
                ))
            return names

        def http_method_not_allowed(self, request, *args, **kwargs):
            logger.warning('Method Not Allowed (%s): %s', request.method, request.path,
                extra={
                    'status_code': 405,
                    'request': self.request
                }
            )
            return http.HttpResponseNotAllowed(self._allowed_methods())

        def options(self, request, *args, **kwargs):
            """
            Handles responding to requests for the OPTIONS HTTP verb.
            """
            response = http.HttpResponse()
            response['Allow'] = ', '.join(self._allowed_methods())
            response['Content-Length'] = '0'
            return response

        def post(self, request, *args, **kwargs):
            """
            Handles POST requests, instantiating a form instance with the passed
            POST variables and then checked for validity.
            """
            form_class = self.get_form_class()
            form = self.get_form(form_class)
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

        def post(self, request, *args, **kwargs):
            self.object = None
            return super(BaseCreateView, self).post(request, *args, **kwargs)

        def put(self, *args, **kwargs):
            return self.post(*args, **kwargs)

        def render_to_response(self, context, **response_kwargs):
            """
            Returns a response, using the `response_class` for this
            view, with a template rendered with the given context.

            If any keyword arguments are provided, they will be
            passed to the constructor of the response class.
            """
            response_kwargs.setdefault('content_type', self.content_type)
            return self.response_class(
                request = self.request,
                template = self.get_template_names(),
                context = context,
                **response_kwargs
            )
