import sys
import requests

from optparse import OptionParser
parser = OptionParser()

#change this!
BASE_URL = "http://127.0.0.1:5000%s"

API_KEY = "CHANGE_ME"

ADD_URL = BASE_URL % '/image/add/'
DEL_URL = BASE_URL % '/image/delete/'

parser.add_option("--action", dest="action",
                          help="add or delete")

def main(action, key, value=None):
    data = {'api_key': API_KEY, 'key': key}
    if action == 'add':
        if not value:
            sys.exit('value is required')
        else:
            data['value'] = value
            response = requests.post(ADD_URL, data = data)

    elif action == 'delete' or action == 'del':
        response = requests.post(DEL_URL, data = data)

    if response.status_code == 200:
        print "uploaded"
    else:
        print "there was an error"


if __name__ == "__main__":
    (options, args) = parser.parse_args()
    if len(args) < 1:
        sys.exit('wrong args number <key, value>')
    main(options.action, *args)
