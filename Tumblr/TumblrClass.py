import requests
from requests_oauthlib import OAuth1, OAuth1Session
import json

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

        if (oauth_key, oauth_key_sec, oauth_token, oauth_token_sec) == ('','','',''):
            self.conf_read(file, quiet)
        else:
            self.oauth_key = oauth_key
            self.oauth_key_sec = oauth_key_sec
            self.oauth_token = oauth_token
            self.oauth_token_sec = oauth_token_sec

            self.check_oauth()

            if not quiet:
                self.keys()
                self.tokens()

    def check_oauth(self):
        if self.oauth_token and self.oauth_token_sec and (not self.oauth_key or not self.oauth_key_sec):
            raise TypeError('Needs both oauth consumer keys if tokens are provided')
        elif bool(self.oauth_token) + bool(self.oauth_token) == 1:
            raise TypeError('Needs both oauth tokens')

        if self.oauth_key == '':
            raise TypeError('Consumer key cannot be empty')

        self.oauth = OAuth1(self.oauth_key, self.oauth_key_sec, self.oauth_token, self.oauth_token_sec)

    def conf_read(self, file='tumblr.conf.json', quiet=True):
        with open(file, 'r') as conf:
            conf = json.load(conf)

            oauth_key = conf.get('oauth_key', '')
            oauth_key_sec = conf.get('oauth_key_sec', '')
            oauth_token = conf.get('oauth_token', '')
            oauth_token_sec = conf.get('oauth_token_sec', '')

            self.oauth_key = oauth_key
            self.oauth_key_sec = oauth_key_sec
            self.oauth_token = oauth_token
            self.oauth_token_sec = oauth_token_sec

            self.check_oauth()

            if not quiet:
                self.keys()
                self.tokens()

    def conf_save(self, file='tumblr.conf.json'):
        oauth = {
            "oauth_key": self.oauth_key,
            "oauth_key_sec": self.oauth_key_sec,
            "oauth_token": self.oauth_token,
            "oauth_token_sec": self.oauth_token_sec
            }
        with open(file, 'w') as conf:
            conf.write(json.dumps(oauth, indent=2)+'\n')

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

        self.check_oauth()

        url  = f"http://api.tumblr.com/v2/blog/{user}.tumblr.com/{section}"
        url += f"?limit={limit}"
        if offset > 0:
            url += f"&offset={offset}"
        elif before > 0:
            url += f"&before={before}"
        elif after > 0:
            url += f"&after={after}"

        get = requests.get(url, auth=self.oauth)
        get = json.loads(get.text)
        get = {
            'user': user,
            'section': section,
            'meta': get['meta'],
            'errors': get.get('errors', [{None: None}]),
            'response': get.get('response', [{None: None}]),
            }

        return get

    def get_tokens(self, save=False, quiet=True):
        tokenurl_request = 'http://www.tumblr.com/oauth/request_token'
        tokenurl_authorize = 'http://www.tumblr.com/oauth/authorize'
        tokenurl_access = 'http://www.tumblr.com/oauth/access_token'

        oauth_session = OAuth1Session(self.oauth_key, self.oauth_key_sec)
        oauth_response = oauth_session.fetch_request_token(tokenurl_request)

        oauth_token = oauth_response['oauth_token']
        oauth_token_sec = oauth_response['oauth_token_secret']

        print("Please go here and authorize:")
        tokenurl_authorize = oauth_session.authorization_url(tokenurl_authorize)
        print(tokenurl_authorize)
        oauth_verifier = input('Paste the full redirect url here: ')
        oauth_verifier = oauth_session.parse_authorization_response(oauth_verifier)
        oauth_verifier = oauth_verifier['oauth_verifier']

        oauth_session = OAuth1Session(self.oauth_key, self.oauth_key_sec,
            oauth_token, oauth_token_sec,
            verifier=oauth_verifier)

        oauth_tokens = oauth_session.fetch_access_token(tokenurl_access)

        self.oauth_token = oauth_tokens.get('oauth_token', '')
        self.oauth_token_sec = oauth_tokens.get('oauth_token_secret', '')

        self.check_oauth()

        if save:
            self.conf_save()
        if not quiet:
            self.tokens()
