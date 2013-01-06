import sys
import requests
import settings

import argparse
parser = argparse.ArgumentParser(description='Subir imagenes!')

ADD_URL = settings.BASE_URL % '/image/add/'
DEL_URL = settings.BASE_URL % '/image/delete/'
LIST_URL = settings.BASE_URL % '/list/'

parser.add_argument("action", help="valid values: add or delete")
parser.add_argument('--key', help='The key value for the url')
parser.add_argument('--url', help='The url to redirect to')

def assert_option(option_name, args):
    if not getattr(args, option_name):
        sys.exit("The option --%s is required" % option_name)

def main(action, key, value=None):
    data = {'api_key': settings.API_KEY, 'key': key}
    if action == 'add':
        data['value'] = value
        response = requests.post(ADD_URL, data = data)
    elif action == 'delete' or action == 'del':
        response = requests.post(DEL_URL, data = data)
    elif action == 'list':
        response = requests.get(LIST_URL)
        print response.content

    if response.status_code == 200:
        print "%s: OK" % action
    else:
        print "there was an error"
        print response.content

if __name__ == "__main__":
    args = parser.parse_args()

    if args.action in ('del', 'delete'):
        assert_option('key', args)

    if args.action == 'add':
        assert_option('key', args)
        assert_option('url', args)

    main(args.action, args.key, args.url)
