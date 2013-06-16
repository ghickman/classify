import pprint
import sys

from library import build

def run():

    # try:
    pprint.pprint(build(sys.argv[1]), width=300)
    # except ImportError:
    #     sys.stderr.write('Could not import: {0}\n'.format(sys.argv[1]))
    #     sys.exit(1)

if __name__ == '__main__':
    run()
