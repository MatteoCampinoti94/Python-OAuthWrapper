import requests
import json
import os

class Tumblr:
    def __init__(self, oauth_key='', oauth_sec=''):
        if type(oauth_key) != str or type(oauth_sec) != str:
            raise TypeError

        if os.path.isfile('backup.conf') and (oauth_key == '' or oauth_sec == ''):
            with open('backup.conf') as conf:
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

    def get(self, user, section, offset=0, limit=20):
        if type(user) != str or type(section) != str:
            raise TypeError
        if type(limit) != int or type(offset) != int:
            raise TypeError

        url  = f"http://api.tumblr.com/v2/blog/{user}.tumblr.com/{section}/"
        url += f"?api_key={self.oauth_key}"
        url += f"&limit={limit}&offset={offset}"

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

    def get_all(self, user, section, limit=0):
        if type(user) != str or type(section) != str:
            raise TypeError
        if type(limit) != int:
            raise TypeError

        total = limit
        if limit <= 0:
            total = self.get_tot(user, section)
        downloads = 0
        items = dict()
        while downloads < total:
            for o in range(0, total, 20):
                get = self.get(user, section, o)
                if section == 'posts':
                    get = get['response'].get('posts', {0: None})
                elif section == 'likes':
                    get = get['response'].get('liked_posts', {0: None})
                get = {k: gk for k,gk in enumerate(get,o)}
                downloads += len(get)
                items.update(get)

            if limit <= 0:
                total = self.get_tot(user, section)

        return {'section': section, 'posts': items}
