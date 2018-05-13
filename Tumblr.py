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

    def get_all(self, user, section, limit=0, quiet=True):
        if type(user) != str or type(section) != str:
            raise TypeError
        if type(limit) != int:
            raise TypeError
        if section not in ('likes', 'posts'):
            print(f'Section "{section}" is not supported')
            return {'user': user, 'section': section, 'posts': {None: None}}

        total = limit
        if limit <= 0:
            total = self.get_tot(user, section)
        items = dict()
        while len(items) < total:
            if len(items):
                time_last = tuple(items.keys())[-1]
                if section == 'posts':
                    time_last = items[time_last]['timestamp']
                elif section == 'likes':
                    time_last = items[time_last]['liked_timestamp']
            else:
                time_last = int(time.time() + 86400)

            get = self.get(user, section, before=time_last)

            if get['status']['code'] == 429:
                if not quiet:
                    print('Rate limit exceded')
                time.sleep(10)
                continue
            elif get['status']['code'] != 200:
                if not quiet:
                    print('code:',get['status']['code'])
                    print('mesg:',get['status']['msg'])
                continue

            if section == 'posts':
                get = get['response'].get('posts', {0: None})
            elif section == 'likes':
                get = get['response'].get('liked_posts', {0: None})

            get = {k: gk for k,gk in enumerate(get,len(items))}
            if len(get) == 0:
                break
            items.update(get)

        return {'user': user, 'section': section, 'posts': items}
