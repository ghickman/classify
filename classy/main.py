import __builtin__
import collections
import inspect
import os
import pprint
import pydoc
import string
import sys


# attribute = {'name': '', 'default': '', 'defined': ''}
# TODO: Method ordering should be done by enumerating the parents list
# method = {'name': '', 'docstring': '', 'order': 0, 'defined': ''}


def docclass(klass, obj, name=None, mod=None, *ignored):
    """Produce text documentation for a given class obj."""
    import pdb;pdb.set_trace()
    realname = obj.__name__
    name = name or realname
    bases = obj.__bases__
    klass['name'] = realname

    def makename(c, m=obj.__module__):
        return pydoc.classname(c, m)

    if name == realname:
        title = 'class ' + realname
    else:
        title = name + ' = class ' + realname
    if bases:
        parents = map(makename, bases)
        title = title + '(%s)' % string.join(parents, ', ')

    doc = pydoc.getdoc(obj)
    klass['docstring'] = doc
    contents = doc and [doc + '\n'] or []
    push = contents.append

    # List the mro, if non-trivial.
    mro = collections.deque(inspect.getmro(obj))
    klass['parents'].extend([k.__name__ for k in mro])
    if len(mro) > 2:
        push("Method resolution order:")
        for base in mro:
            push('    ' + makename(base))
        push('')

    def spill(msg, attrs, predicate):
        ok, attrs = pydoc._split_list(attrs, predicate)
        if ok:
            push(msg)
            for name, kind, homecls, value in ok:
                push(dispatch(getattr(obj, name),
                                   name, mod, obj))
        return attrs

    def spilldescriptors(msg, attrs, predicate):
        ok, attrs = pydoc._split_list(attrs, predicate)
        if ok:
            push(msg)
            for name, kind, homecls, value in ok:
                push(_docdescriptor(name, value, mod))
        return attrs

    def spilldata(msg, attrs, predicate):
        ok, attrs = pydoc._split_list(attrs, predicate)
        for attr in ok:
            klass['attributes'].append(build_attributes(obj, ok))

        if ok:
            push(msg)
            for name, kind, homecls, value in ok:
                if (hasattr(value, '__call__') or
                        inspect.isdatadescriptor(value)):
                    # TODO: Work out when/why this is called
                    doc = pydoc.getdoc(value)
                else:
                    doc = None
                push(docother(getattr(obj, name),
                              name, mod, maxlen=70, doc=doc) + '\n')
        return attrs

    attrs = filter(lambda data: pydoc.visiblename(data[0], obj=obj),
                   pydoc.classify_class_attrs(obj))

    # everything runs from this loop
    while attrs:
        if mro:
            thisclass = mro.popleft()
        else:
            thisclass = attrs[0][2]
        attrs, inherited = pydoc._split_list(attrs, lambda t: t[2] is thisclass)

        if thisclass is __builtin__.object:
            attrs = inherited
            continue

        attrs.sort()  # Sort attrs by name.

        ## ATTRIBUTES
        for a in build_attributes(filter(lambda t: t[1] == 'data', attrs), obj):
            klass['attributes'].append(a)

        ## METHODS
        is_method = lambda t: (t[1] == 'method' or
                               t[1] == 'class method' or
                               t[1] == 'static method')
        for method in build_methods(filter(is_method, attrs), klass['parents']):
            klass['methods'].append(method)

        descriptors = filter(lambda t: t[1] == 'data descriptor', attrs)

        attrs = inherited

    return klass

def formatvalue(obj):
    """Format an argument default value as text."""
    return '=' + repr(obj)

def docroutine(klass, obj, name=None, mod=None, cl=None):
    """Produce text documentation for a function or method obj."""
    realname = obj.__name__
    name = name or realname
    note = ''
    if inspect.ismethod(obj):
        imclass = obj.im_class
        if cl:
            if imclass is not cl:
                note = ' from ' + pydoc.classname(imclass, mod)
        else:
            if obj.im_self is not None:
                note = ' method of %s instance' % pydoc.classname(
                    obj.im___class__, mod)
            else:
                note = ' unbound %s method' % pydoc.classname(imclass,mod)
        obj = obj.im_func

    if name == realname:
        title = realname
    else:
        title = name + ' = ' + realname
    if inspect.isfunction(obj):
        args, varargs, varkw, defaults = inspect.getargspec(obj)
        argspec = inspect.formatargspec(
            args, varargs, varkw, defaults, formatvalue=formatvalue)
        if realname == '<lambda>':
            title = name + ' lambda '
            argspec = argspec[1:-1] # remove parentheses
    else:
        argspec = '(...)'

    return klass

def _docdescriptor(klass, name, value, mod):
    results = []
    push = results.append

    if name:
        push(name)
        push('\n')
    doc = pydoc.getdoc(value) or ''
    if doc:
        push(doc)
        push('\n')
    return ''.join(results)

def docproperty(klass, obj, name=None, mod=None, cl=None):
    """Produce text documentation for a property."""
    return _docdescriptor(klass, name, obj, mod)

def docdata(klass, obj, name=None, mod=None, cl=None):
    """Produce text documentation for a data descriptor."""
    return _docdescriptor(klass, name, obj, mod)

def docother(klass, obj, name=None, mod=None, parent=None, maxlen=None, doc=None):
    """Produce text documentation for a data obj."""
    r = repr(obj)
    if maxlen:
        line = (name and name + ' = ' or '') + r
        chop = maxlen - len(line)
        if chop < 0: r = r[:chop] + '...'
    line = (name and name + ' = ' or '') + r
    if doc is not None:
        line += '\n' + str(doc)
    return line

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
        yield {
            'name': method[0],
            'docstring': pydoc.getdoc(method[3]),
            'order': parents.index(method[2].__name__),
            'defined': method[2].__name__,
        }


def dispatch(klass, obj, name=None, *args):
    """Generate documentation for an obj."""
    args = (klass, obj, name) + args
    # 'try' clause is to attempt to handle the possibility that inspect
    # identifies something in a way that pydoc itself has issues handling;
    # think 'super' and how it is a descriptor (which raises the exception
    # by lacking a __name__ attribute) and an instance.
    if inspect.isgetsetdescriptor(obj): return docdata(*args)
    if inspect.ismemberdescriptor(obj): return docdata(*args)
    try:
        if inspect.isclass(obj): return docclass(*args)
        if inspect.isroutine(obj): return docroutine(*args)
    except AttributeError:
        pass
    if isinstance(obj, property): return docproperty(*args)
    return docother(*args)

def run(thing, forceload=0):
    """Render text documentation, given an obj or a path to an obj."""
    klass = {
        'attributes': [],
        'methods': [],
        'properties': [],
        'parents': [],
    }

    obj, name = pydoc.resolve(thing, forceload)
    desc = pydoc.describe(obj)
    module = inspect.getmodule(obj)
    if name and '.' in name:
        desc += ' in ' + name[:name.rfind('.')]
    elif module and module is not obj:
        desc += ' in module ' + module.__name__
    if type(obj) is pydoc._OLD_INSTANCE_TYPE:
        # If the passed obj is an instance of an old-style class,
        # dispatch its available methods instead of its value.
        obj = obj.__class__
    elif not (inspect.ismodule(obj) or
              inspect.isclass(obj) or
              inspect.isroutine(obj) or
              inspect.isgetsetdescriptor(obj) or
              inspect.ismemberdescriptor(obj) or
              isinstance(obj, property)):
        # If the passed obj is a piece of data or an instance,
        # dispatch its available methods instead of its value.
        print('instance')
        obj = type(obj)
    return dispatch(klass, obj, name)

if __name__ == '__main__':
    if any([arg.startswith('django') for arg in sys.argv[1:]]):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'contrib.django.settings'
    pprint.pprint(run(sys.argv[1]))
