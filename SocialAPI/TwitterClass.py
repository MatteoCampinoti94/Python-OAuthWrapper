import base64
import requests
from urllib.parse import quote_plus
from .APIBase import APIBase

def json_parser(data, req_url, parameters):
    status = data.status_code

    response = {
        'request': req_url,
        'parameters': parameters,
        'status_code': status,
        'headers': data.headers
        }

    if data.text:
        response['response'] = data.json()
    else:
        response['response'] = data.text

    return response

class Twitter(APIBase):
    api_url = 'https://api.twitter.com/1.1/'
    tokenurl_request = 'https://api.twitter.com/oauth/request_token'
    tokenurl_authorize = 'https://api.twitter.com/oauth/authorize'
    tokenurl_access = 'https://api.twitter.com/oauth/access_token'
    tokenurl_oauth2 = 'https://api.twitter.com/oauth2/token'
    oauthv = 2

    def GetTokens(self, save=False, file='', quiet=True):
        self.GetOAuth1Tokens('pin', save, file, quiet)

    def GetAppAuth(self, save=False, quiet=True, file=''):
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
        self.api_oauth()

        if save:
            self.conf_save(file)
        if not quiet:
            self.tokens()

    def ratelimit(self, raw=False, **params):
        req_url = '/application/rate_limit_status.json'
        valid_params = ['resources']

        response = self.APIRequest('GET', req_url, params, valid_params)

        if raw:
            return response
        else:
            return json_parser(response, req_url, params)

    def favorites(self, raw=False, **params):
        req_url = '/favorites/list.json'
        valid_params = ['user_id', 'screen_name', 'count', 'since_id', 'max_id', 'include_entities']

        response = self.APIRequest('GET', req_url, params, valid_params)

        if raw:
            return response
        else:
            return json_parser(response, req_url, params)

    def favoritecreate(self, raw=False, **params):
        req_url = '/favorites/create.json'
        valid_params = ['id','include_entities']

        response = self.APIRequest('POST', req_url, params, valid_params)

        if raw:
            return response
        else:
            return json_parser(response, req_url, params)

    def favoritedestroy(self, raw=False, **params):
        req_url = '/favorites/destroy.json'
        valid_params = ['id','include_entities']

        response = self.APIRequest('POST', req_url, params, valid_params)

        if raw:
            return response
        else:
            return json_parser(response, req_url, params)
