import argparse
import os
import SimpleHTTPServer
import SocketServer
import sys
import webbrowser

from jinja2 import Environment, PackageLoader

from library import build


parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('klass', metavar='KLASS')
parser.add_argument('-s', '--serve', action='store_true', dest='serve')
parser.add_argument('-p', '--port', action='store', dest='port', type=int, default=8000)
args = parser.parse_args()


def serve(port):
    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer(('', port), Handler)
    print 'Serving on port: {0}'.format(port)
    webbrowser.open_new_tab('http://localhost:{0}/classify.html'.format(port))
    httpd.serve_forever()


def run():
    try:
        structure = build(args.klass)
    except ImportError:
        sys.stderr.write('Could not import: {0}\n'.format(sys.argv[1]))
        sys.exit(1)

    env = Environment(loader=PackageLoader('classify', ''))
    output = env.get_template('template.html').render(klass=structure)

    path = os.path.join(os.getcwd(), 'output')
    if not os.path.exists(path):
        os.makedirs(path)
    with open(os.path.join(path, 'classify.html'), 'w') as f:
        f.write(output)

    if args.serve:
        serve(args.port)


if __name__ == '__main__':
    run()
