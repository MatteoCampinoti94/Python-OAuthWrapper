import base64
import requests
from urllib.parse import urlencode, quote_plus
from .APIBase import APIBase

class Twitter(APIBase):
    api_url = 'https://api.twitter.com/1.1/'
    tokenurl_request = 'http://api.twitter.com/oauth/request_token'
    tokenurl_authorize = 'http://api.twitter.com/oauth/authorize'
    tokenurl_access = 'http://api.twitter.com/oauth/access_token'
    oauthv = 2

    def get_tokens(self, save, quiet, file='twitter.conf.json'):
        key = quote_plus(self.oauth_key)
        secret = quote_plus(self.oauth_key_sec)
        bearer_token = base64.b64encode(f'{key}:{secret}'.encode('utf8'))

        post_headers = {
            'Authorization': f"Basic {bearer_token.decode('utf8')}",
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        }

        res = requests.post(url='https://api.twitter.com/oauth2/token',
                            data={'grant_type': 'client_credentials'},
                            headers=post_headers)

        self.oauth2_token = res.json()

        if save:
            self.conf_save(file)
        if not quiet:
            self.tokens()

    # def favorites(self, **params):
    #     req_url = '/favorites/list.json'
    #     valid_params = ['user_id', 'screen_name', 'count', 'since_id', 'max_id', 'include_entities']
    #
    #     return self.api_request('GET', req_url, params, valid_params)
