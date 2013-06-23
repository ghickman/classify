import string


def html(structure, template, serve, port):
    return template.render(klass=structure)


def paged(structure):
    INDENT = ' '*4

    def attributes(attributes):
        attrs = []
        for name, definitions in attributes.items():
            obj = definitions[-1]['object']
            attrs.append('{0}{1} = {2}\n'.format(INDENT, name, obj))
        return string.join(attrs, '')

    def declaration(name, parents):
        parents = string.join([p.__name__ for p in parents], ', ')
        return 'class {0}({1}):'.format(name, parents)

    def docstring(docstring):
        quotes = '{0}"""\n'.format(INDENT)
        lines = docstring.split('\n')
        block = string.join(['{0}{1}\n'.format(INDENT, line) for line in lines], '')
        return '{0}{1}{2}'.format(quotes, block, quotes)

    def methods(methods):
        content = ''
        for name, definitions in methods.items():
            for d in definitions:
                lines = d['code'].split('\n')[:-1]
                for line in lines:
                    content += '{0}{1}\n'.format(INDENT, line[4:])
                content += '\n'
        return content

    def parents(parents):
        return string.join([p.__name__ for p in parents], ', ')


    content = declaration(structure['name'], structure['parents'])
    content += '\n'
    if docstring:
        content += docstring(structure['docstring'])
    content += attributes(structure['attributes'])
    content += '\n'
    content += methods(structure['methods'])
    return content
