import requests
import time
import json
import os

class Tumblr:
    def __init__(self, oauth_key='', oauth_sec='', file='tumblr.conf', quiet=True):
        if type(oauth_key) != str or type(oauth_sec) != str or type(file) != str:
            raise TypeError

        if os.path.isfile(file) and (oauth_key == '' or oauth_sec == ''):
            with open(file) as conf:
                conf = [c.strip().replace(' ', '') for c in conf.readlines()]

            # Check each read line and split them around the = sign if they starts with one of the settings
            for c in conf:
                if c.startswith('oauth_key='):
                    oauth_key = c.split('=')[1]
                elif c.startswith('oauth_sec='):
                    oauth_sec = c.split('=')[1]

        self.oauth_key = oauth_key
        self.oauth_sec = oauth_sec

        if oauth_key == '' or oauth_sec == '':
            raise TypeError

        if not quiet:
            self.keys()

    def keys(self):
        print(f'Consumer key = {self.oauth_key}')
        print(f'Secret key = {self.oauth_sec}')

    def get(self, user, section, limit=20, offset=0, before=0, after=0):
        if type(user) != str or type(section) != str:
            raise TypeError
        if any(type(arg) != int for arg in (limit, offset, before, after)):
            raise TypeError

        url  = f"http://api.tumblr.com/v2/blog/{user}.tumblr.com/{section}/"
        url += f"?api_key={self.oauth_key}"
        url += f"&limit={limit}"
        if offset > 0:
            url += f"&offset={offset}"
        elif before > 0:
            url += f"&before={before}"
        elif after > 0:
            url += f"&after={after}"

        get = requests.get(url)
        get = json.loads(get.text)
        get = {
            'user': user,
            'section': section,
            'status': {
                'code': get['meta']['status'],
                'msg': get['meta']['msg'],
                },
            'errors': get.get('errors', {None: None}),
            'response': get.get('response', {None: None}),
            }

        return get

    def get_tot(self, user, section):
        if section == 'posts':
            total = self.get(user, section, 0, 0)['response'].get('total_posts', 0)
        elif section == 'likes':
            total = self.get(user, section, 0, 0)['response'].get('liked_count', 0)
        else:
            total = 0

        return total
