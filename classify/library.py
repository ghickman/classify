import __builtin__
import collections
import inspect
import operator
import os
import pydoc


def classify(klass, obj, name=None, mod=None, *ignored):
    if not inspect.isclass(obj):
        raise Exception

    mro = collections.deque(inspect.getmro(obj))

    klass.update({
        'name': obj.__name__,
        'docstring': pydoc.getdoc(obj),
        'parents': [k.__name__ for k in mro]
    })

    def get_attrs(obj):
        all_attrs = filter(lambda data: pydoc.visiblename(data[0], obj=obj),
                      pydoc.classify_class_attrs(obj))
        return filter(lambda data: data[2] == obj, all_attrs)

    for cls in mro:
        if cls is __builtin__.object:
            continue

        attrs = get_attrs(cls)

        ## ATTRIBUTES
        for a in build_attributes(filter(lambda t: t[1] == 'data', attrs), obj):
            klass['attributes'].append(a)

        ## METHODS
        is_method = lambda t: (t[1] == 'method' or
                               t[1] == 'class method' or
                               t[1] == 'static method')
        for method in build_methods(filter(is_method, attrs), klass['parents']):
            klass['methods'].append(method)

        # descriptors = filter(lambda t: t[1] == 'data descriptor', attrs)

    return klass

def build_attributes(attributes, obj):
    """Build the Attribute list for the given object."""
    for attr in attributes:
        yield {
            'name': attr[0],
            'default': getattr(obj, attr[0]),
            'defined': attr[2].__name__,
        }

def build_methods(methods, parents):
    for method in methods:
        func = getattr(method[2], method[0])
        # Get the method arguments
        args, varargs, keywords, defaults = inspect.getargspec(func)
        arguments = inspect.formatargspec(args, varargs=varargs, varkw=keywords, defaults=defaults)

        # Get source line details
        lines, start_line = inspect.getsourcelines(func)

        yield {
            'name': method[0],
            'docstring': pydoc.getdoc(method[3]),
            'order': parents.index(method[2].__name__),
            'defined': method[2].__name__,
            'arguments': arguments,
            'code': ''.join(lines),
            'lines': {'start': start_line, 'total': len(lines)},
            'file': inspect.getsourcefile(func)
        }

def sort_structures(klass):
    for lst in ('attributes', 'methods'):
        klass[lst] = sorted(klass[lst], key=operator.itemgetter('name'))
    return klass

def build(thing):
    """Build a dictionary mapping of a class."""
    if 'django' in thing:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'classify.contrib.django.settings'

    klass = {
        'attributes': [],
        'methods': [],
        'properties': [],
        'parents': [],
    }

    obj, name = pydoc.resolve(thing, forceload=0)
    if type(obj) is pydoc._OLD_INSTANCE_TYPE:
        # If the passed obj is an instance of an old-style class,
        # dispatch its available methods instead of its value.
        obj = obj.__class__
    return sort_structures(classify(klass, obj, name))
