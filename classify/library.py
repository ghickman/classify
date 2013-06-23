import __builtin__
import collections
import inspect
import os
import pydoc
import sys


class DefaultOrderedDict(collections.OrderedDict):
    def __init__(self, default_factory=None, *a, **kw):
        if (default_factory is not None and
            not isinstance(default_factory, collections.Callable)):
            raise TypeError('first argument must be callable')
        collections.OrderedDict.__init__(self, *a, **kw)
        self.default_factory = default_factory

    def __getitem__(self, key):
        try:
            return collections.OrderedDict.__getitem__(self, key)
        except KeyError:
            return self.__missing__(key)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = value = self.default_factory()
        return value

    def __reduce__(self):
        if self.default_factory is None:
            args = tuple()
        else:
            args = self.default_factory,
        return type(self), args, None, None, self.items()

    def copy(self):
        return self.__copy__()

    def __copy__(self):
        return type(self)(self.default_factory, self)

    def __deepcopy__(self, memo):
        import copy
        return type(self)(self.default_factory,
                          copy.deepcopy(self.items()))
    def __repr__(self):
        return 'OrderedDefaultDict({0}, {1})'.format(self.default_factory,
                                        collections.OrderedDict.__repr__(self))


def classify(klass, obj, name=None, mod=None, *ignored):
    if not inspect.isclass(obj):
        raise Exception

    mro = list(reversed(inspect.getmro(obj)))

    klass.update({
        'name': obj.__name__,
        'docstring': pydoc.getdoc(obj),
        'ancestors': [k.__name__ for k in mro],
        'parents': inspect.getclasstree([obj])[-1][0][1]
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
        for attribute in build_attributes(filter(lambda t: t[1] == 'data', attrs), obj):
            name = attribute.pop('name')
            klass['attributes'][name].append(attribute)

        ## METHODS
        is_method = lambda t: (t[1] == 'method' or
                               t[1] == 'class method' or
                               t[1] == 'static method')
        for method in build_methods(filter(is_method, attrs)):
            name = method.pop('name')
            klass['methods'][name].append(method)

        # descriptors = filter(lambda t: t[1] == 'data descriptor', attrs)

    return klass

def build_attributes(attributes, obj):
    """Build the Attribute list for the given object."""
    for attr in attributes:
        yield {
            'name': attr[0],
            'object': getattr(attr[2], attr[0]),
            'defining_class': attr[2],
        }

def build_methods(methods):
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
            'defining_class': method[2],
            'arguments': arguments,
            'code': ''.join(lines),
            'lines': {'start': start_line, 'total': len(lines)},
            'file': inspect.getsourcefile(func)
        }

def build(thing):
    """Build a dictionary mapping of a class."""
    if 'django' in thing:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'classify.contrib.django.settings'

    sys.path.insert(0, '')

    klass = {
        'attributes': DefaultOrderedDict(list),
        'methods': DefaultOrderedDict(list),
        'properties': [],
        'ancestors': [],
        'parents': [],
    }

    obj, name = pydoc.resolve(thing, forceload=0)
    if type(obj) is pydoc._OLD_INSTANCE_TYPE:
        # If the passed obj is an instance of an old-style class,
        # dispatch its available methods instead of its value.
        obj = obj.__class__
    return classify(klass, obj, name)
