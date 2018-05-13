import requests
import json
import os, sys

class Tumblr:
    def __init__(self, user, oauth_key, oauth_sec):
        if any(type(arg) != str for arg in (user, oauth_key, oauth_sec)):
            raise TypeError
        if any(arg == '' for arg in (user, oauth_key, oauth_sec)):
            raise TypeError

        self._user = user
        self._oauth_key = oauth_key
        self._oauth_sec = oauth_sec

    def get(self, section, offset=0, limit=20):
        if type(section) != str:
            raise TypeError
        if type(limit) != int or type(offset) != int:
            raise TypeError

        url  = f"http://api.tumblr.com/v2/blog/{user}.tumblr.com/{section}"
        url += f"?api_key={oauth_key}"
        url += f"&limit={limit}&offset={offset}"

        response = requests.get(url)
        response = json.loads(response.text)
        response = {
            'section': section,
            'status': {
                'code': response['meta']['status'],
                'msg': response['meta']['msg'],
                },
            'errors': response.get('errors', None),
            'data': response.get('response', None),
            }

        return response

# Variable declaration
user = str()
oauth_key = str()
oauth_sec = str()

# If file exsts read all lines, strip and remove spaces
if os.path.isfile('backup.conf'):
    with open('backup.conf') as conf:
        conf = [c.strip().replace(' ', '') for c in conf.readlines()]

    # Check each read line and split them around the = sign if they starts with one of the settings
    for c in conf:
        if c.startswith('user='):
            user = c.split('=')[1]
        if c.startswith('oauth_key='):
            oauth_key = c.split('=')[1]
        if c.startswith('oauth_sec='):
            oauth_sec = c.split('=')[1]

# Print which variables remained empty and exit if any is
if not user:
    print('ERROR: user not defined')
if not oauth_key:
    print('ERROR: oauth key not defined')
if not oauth_sec:
    print('ERROR: oauth secret key not defined')
if not user or not oauth_key or not oauth_sec:
    sys.exit(1)
else:
    print('user =', user)
    print('oauth_key =', oauth_key)
    print('oauth_sec =', oauth_sec)

# Declare tumblr object
tumblr = Tumblr(user, oauth_key, oauth_sec)

# Get likes using class and print response and message
likes = tumblr.get('likes', 0, 1)
print(likes['status'])
print(likes['errors'])
print(likes['data'])
