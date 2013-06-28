import argparse
import collections
import os
import pkg_resources
import pydoc
import SimpleHTTPServer
import SocketServer
import sys
import webbrowser

from jinja2 import Environment, PackageLoader

from .library import build
from .formatters import html, paged


version = pkg_resources.get_distribution('classify').version


parser = argparse.ArgumentParser(version='Classify {0}'.format(version))
parser.add_argument('klass', metavar='KLASS')
parser.add_argument('--html', action='store_true', dest='html')
parser.add_argument('--django', action='store_true', dest='django')
parser.add_argument('--django-settings', action='store', dest='django_settings')
parser.add_argument('--output', '-o', action='store', dest='output',
                    default='output', help='Relative path for output files to be saved')
parser.add_argument('-p', '--port', action='store', dest='port', type=int, default=8000)
parser.add_argument('-s', '--serve', action='store_true', dest='serve')
args = parser.parse_args()


def output_path():
    path = os.path.join(os.getcwd(), args.output)
    if not os.path.exists(path):
        os.makedirs(path)
    return os.path.join(path, 'classify.html')


def serve(port):
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(('', port), Handler)
    print('Serving on port: {0}'.format(port))
    webbrowser.open_new_tab('http://localhost:{0}/'
                            'output/classify.html'.format(port))
    httpd.serve_forever()


def run():
    if args.django:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'classify.contrib.django.settings'

    if args.django_settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = args.django_settings

    try:
        structure = build(args.klass)
    except ImportError:
        sys.stderr.write('Could not import: {0}\n'.format(sys.argv[1]))
        sys.exit(1)

    for name, lst in structure['attributes'].items():
        for i, definition in enumerate(lst):
            a = definition['defining_class']
            structure['attributes'][name][i]['defining_class'] = a.__name__

            if isinstance(definition['object'], list):
                try:
                    s = '[{0}]'.format(', '.join([c.__name__ for c in definition['object']]))
                except AttributeError:
                    pass
                else:
                    structure['attributes'][name][i]['default'] = s
                    continue

    sorted_attributes = sorted(structure['attributes'].items(), key=lambda t: t[0])
    structure['attributes'] = collections.OrderedDict(sorted_attributes)

    sorted_methods = sorted(structure['methods'].items(), key=lambda t: t[0])
    structure['methods'] = collections.OrderedDict(sorted_methods)

    env = Environment(loader=PackageLoader('classify', 'templates'))
    if args.html:
        template = env.get_template('web.html')
        output = html(structure, template, serve=args.serve, port=args.port)

        with open(output_path(), 'w') as f:
            f.write(output)

        if args.serve:
            serve(args.port)
    else:
        pydoc.pager(paged(structure))

    sys.exit(0)


if __name__ == '__main__':
    run()
