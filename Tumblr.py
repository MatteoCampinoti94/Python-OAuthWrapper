import requests
import json
import os

class Tumblr:
    def __init__(self, api_key='', api_sec='', oauth_token='', oauth_sec='', file='tumblr.conf', quiet=True):
        if type(api_key) != str or type(api_sec) != str:
            raise TypeError('Api keys need to be passed as strings')
        if type(oauth_token) != str or type(oauth_sec) != str:
            raise TypeError('OAuth tokens need to be passed as strings')
        if type(file) != str:
            raise TypeError('Conf file needs to be passed string')
        if type(quiet) != bool:
            raise TypeError('quiet argument needs to be of type bool')

        if os.path.isfile(file) and (api_key == '' or api_sec == ''):
            with open(file) as conf:
                conf = [c.strip().replace(' ', '') for c in conf.readlines()]

            # Check each read line and split them around the = sign if they starts with one of the settings
            for c in conf:
                if c.startswith('api_key='):
                    api_key = c.split('=')[1]
                elif c.startswith('api_sec='):
                    api_sec = c.split('=')[1]

        self.api_key = api_key
        self.api_sec = api_sec
        self.keys = (self.api_key, self.api_sec)
        self.oauth_token = oauth_token
        self.oauth_sec = oauth_sec
        self.tokens = (self.oauth_token, self.oauth_sec)

        if api_key == '':
            raise TypeError('Consumer key cannot be empty')

        if not quiet:
            self.keys()

    def keys(self):
        print(f'Consumer key = {self.api_key}\nSecret key = {self.api_sec}')

    def get(self, user, section, limit=20, offset=0, before=0, after=0):
        if type(user) != str or type(section) != str:
            raise TypeError('User and section must be passed as strings')
        if any(type(arg) != int for arg in (limit, offset, before, after)):
            raise TypeError('limit, offset, before and after arguments need to be int')
        if bool(offset) + bool(before) + bool(after) > 1:
            raise TypeError('Can only pass either offset, before or after')

        url  = f"http://api.tumblr.com/v2/blog/{user}.tumblr.com/{section}"
        url += f"?api_key={self.api_key}"
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
            'meta': get['meta'],
            'errors': get.get('errors', [{None: None}]),
            'response': get.get('response', [{None: None}]),
            }

        return get

    def get_tot(self, user, section):
        if section.startswith('posts'):
            total = self.get(user, section, 0, 0)['response'].get('total_posts', 0)
        elif section.startswith('likes'):
            total = self.get(user, section, 0, 0)['response'].get('liked_count', 0)
        else:
            total = 0

        return total
