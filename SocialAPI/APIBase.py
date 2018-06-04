import json
import requests
from requests_oauthlib import OAuth1, OAuth1Session, OAuth2, OAuth2Session
from urllib.parse import urlencode

class APIBase:
    def __init__(self, oauth_key='', oauth_key_sec='', oauth_token='', oauth_token_sec='', file='', quiet=True):
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

    def conf_read(self, file='', quiet=True):
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

    def conf_save(self, file=''):
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

    def check_oauth(self):
        if self.oauth_token and self.oauth_token_sec and (not self.oauth_key or not self.oauth_key_sec):
            raise TypeError('Needs both oauth consumer keys if tokens are provided')
        elif bool(self.oauth_token) + bool(self.oauth_token) == 1:
            raise TypeError('Needs both oauth tokens')

        if self.oauth_key == '':
            raise TypeError('Consumer key cannot be empty')

        if self.oauthv == 1:
            self.oauth = OAuth1(self.oauth_key, self.oauth_key_sec, self.oauth_token, self.oauth_token_sec)
        elif self.oauthv == 2:
            raise TypeError('OAuth2 not implemented yet')

    def api_tokens_oauth1(self, save, quiet, file=''):
        tokenurl_request = self.tokenurl_request
        tokenurl_authorize = self.tokenurl_authorize
        tokenurl_access = self.tokenurl_access

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
            self.conf_save(file)
        if not quiet:
            self.tokens()

    def api_tokens_oauth2(self, save, quiet, file=''):
        raise TypeError('OAuth2 not implemented yet')

    def api_request(self, mode, req_url, params={}, valid_params=[]):
        if type(mode) != str or type(req_url) != str:
            raise TypeError('URL and mode must be passed as strings')

        self.check_oauth()

        params = {k: params[k] for k in params if k in valid_params}
        params = urlencode(params)
        req_url = req_url.strip('/') + '/?'*bool(params)+params

        if mode == 'GET':
            get = requests.get(self.api_url+req_url, auth=self.oauth)
            get = json.loads(get.text)
            get = {
                'request': req_url,
                'meta': get['meta'],
                'errors': get.get('errors', [{None: None}]),
                'response': get.get('response', [{None: None}]),
                }

            return get
        elif mode == 'GET-BINARY':
            get = bytes()
            get_stream = requests.get(self.api_url+req_url, auth=self.oauth, stream=True)
            for chunk in get_stream.iter_content(chunk_size=1024):
                get += chunk

            return get
