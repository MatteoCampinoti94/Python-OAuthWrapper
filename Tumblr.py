import requests
import oauth2
from requests_oauthlib import OAuth1
import urllib.parse as urlparse
import json
import os

class Tumblr:
    def __init__(self, oauth_key='', oauth_key_sec='', oauth_token='', oauth_token_sec='', file='tumblr.conf.json', quiet=True):
        if type(oauth_key) != str or type(oauth_key_sec) != str:
            raise TypeError('Api keys need to be passed as strings')
        if type(oauth_token) != str or type(oauth_token_sec) != str:
            raise TypeError('OAuth tokens need to be passed as strings')
        if type(file) != str:
            raise TypeError('Conf file needs to be passed as string')
        if type(quiet) != bool:
            raise TypeError('quiet argument needs to be of type bool')

        if os.path.isfile(file) and oauth_key == '':
            with open(file, 'r') as conf:
                try:
                    conf = json.load(conf)
                    oauth_key = conf.get('oauth_key', '')
                    oauth_key_sec = conf.get('oauth_key_sec', '')
                    oauth_token = conf.get('oauth_token', '')
                    oauth_token_sec = conf.get('oauth_token_sec', '')
                except:
                    raise TypeError(f'"{file}" contains errors')


        self.oauth_key = oauth_key
        self.oauth_key_sec = oauth_key_sec
        self.oauth_keys = (self.oauth_key, self.oauth_key_sec)
        self.oauth_token = oauth_token
        self.oauth_token_sec   = oauth_token_sec
        self.oauth_tokens = (self.oauth_token, self.oauth_token_sec)

        if self.oauth_token and self.oauth_token_sec:
            self.oauth = OAuth1(self.oauth_key, self.oauth_key_sec, self.oauth_token, self.oauth_token_sec)
        else:
            self.oauth = None

        if bool(self.oauth_token) + bool(self.oauth_token) == 1:
            raise TypeError('Only one token was provided, needs both')

        if oauth_key == '':
            raise TypeError('Consumer key cannot be empty')

        if not quiet:
            self.keys()
            self.tokens()

    def keys(self):
        print(f'Consumer key = {self.oauth_key}\nConsumer secret key = {self.oauth_key_sec}')

    def tokens(self):
        print(f'OAuth token = {self.oauth_token}\nOAuth secret token = {self.oauth_token_sec}')

    def get(self, user, section, limit=20, offset=0, before=0, after=0):
        if type(user) != str or type(section) != str:
            raise TypeError('User and section must be passed as strings')
        if any(type(arg) != int for arg in (limit, offset, before, after)):
            raise TypeError('limit, offset, before and after arguments need to be integers')
        if bool(offset) + bool(before) + bool(after) > 1:
            raise TypeError('Can only pass either offset, before or after')

        url  = f"http://api.tumblr.com/v2/blog/{user}.tumblr.com/{section}"
        url += f"?limit={limit}"
        if offset > 0:
            url += f"&offset={offset}"
        elif before > 0:
            url += f"&before={before}"
        elif after > 0:
            url += f"&after={after}"

        if self.oauth:
            get = requests.get(url, auth=self.oauth)
        else:
            get = requests.get(url+f"?oauth_key={self.oauth_key}")
        get = json.loads(get.text)
        get = {
            'user': user,
            'section': section,
            'meta': get['meta'],
            'errors': get.get('errors', [{None: None}]),
            'response': get.get('response', [{None: None}]),
            }

        return get

    def get_tokens(self):
        tokenurl_request = 'http://www.tumblr.com/oauth/request_token'
        tokenurl_authorize = 'http://www.tumblr.com/oauth/authorize'
        tokenurl_access = 'http://www.tumblr.com/oauth/access_token'

        oauth_key = self.oauth_key
        oauth_key_sec = self.oauth_key_sec

        consumer = oauth2.Consumer(oauth_key, oauth_key_sec)
        client = oauth2.Client(consumer)

        response, content = client.request(tokenurl_request, "GET")
        content = content.decode()
        request_token = dict(urlparse.parse_qsl(content))

        print("Go to the following link in your browser:")
        print("{tokenurl_authorize}?oauth_token={request_token['oauth_token']}")
        oauth_verifier = input('Paste the oaut_verifier: ')

        token = oauth2.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        client = oauth2.Client(consumer, token)

        response, content = client.request(tokenurl_access, "GET")
        content = content.decode()
        access_token = dict(urlparse.parse_qsl(content))

        self.oauth_token = access_token.get('oauth_token', '')
        self.oauth_token_sec = access_token.get('oauth_token_secret', '')
        self.oauth_tokens = (self.oauth_token, self.oauth_token_sec)

        if self.oauth_token and self.oauth_token_sec:
            self.oauth = OAuth1(self.oauth_key, self.oauth_key_sec, self.oauth_token, self.oauth_token_sec)
        else:
            self.oauth = None

        if not quiet:
            self.tokens()

    def get_tot(self, user, section):
        if section.startswith('posts'):
            total = self.get(user, section, 0, 0)['response'].get('total_posts', 0)
        elif section.startswith('likes'):
            total = self.get(user, section, 0, 0)['response'].get('liked_count', 0)
        else:
            total = 0

        return total
