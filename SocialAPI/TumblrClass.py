from requests_oauthlib import OAuth1Session
from .APIBase import APIBase

def json_parser(data, req_url, parameters):
    response = data.json()
    response = {
        'request': req_url,
        'parameters': parameters,
        'headers': data.headers,
        'meta': response['meta'],
        'errors': response.get('errors', [{}]),
        'response': response.get('response', [{}]),
        }

    return response

class Tumblr(APIBase):
    api_url = 'https://api.tumblr.com/v2/'
    tokenurl_request = 'http://www.tumblr.com/oauth/request_token'
    tokenurl_authorize = 'http://www.tumblr.com/oauth/authorize'
    tokenurl_access = 'http://www.tumblr.com/oauth/access_token'
    oauthv = 1

    def GetTokens(self, save=False, file='', quiet=True):
        self.GetOAuth1Tokens('url', save, file, quiet)

    def info(self, blog='', raw=False):
        if blog:
            req_url = f'/blog/{blog}.tumblr.com/info'
        else:
            req_url = '/user/info'

        response =  self.APIRequest('GET', req_url)
        if raw:
            return response
        else:
            return json_parser(response, req_url, params)

    def likes(self, blog='', raw=False, **params):
        if blog:
            req_url = f'/blog/{blog}.tumblr.com/likes'
        else:
            req_url = '/user/likes'
        valid_params = ['limit', 'offset', 'before', 'after']

        response =  self.APIRequest('GET', req_url, params, valid_params)
        if raw:
            return response
        else:
            return json_parser(response, req_url, params)

    def following(self, blog='', raw=False, **params):
        if blog:
            req_url = f'/blog/{blog}.tumblr.com/following'
        else:
            req_url = '/user/following'
        valid_params = ['limit', 'offset']

        response =  self.APIRequest('GET', req_url, params, valid_params)
        if raw:
            return response
        else:
            return json_parser(response, req_url, params)

    def dashboard(self, **params):
        req_url = '/user/dashboard'
        valid_params = ['limit', 'offset', 'type', 'since_id', 'reblog_info', 'notes_info']

        response =  self.APIRequest('GET', req_url, params, valid_params)
        if raw:
            return response
        else:
            return json_parser(response, req_url, params)

    def posts(self, blog, type='', raw=False, **params):
        req_url = f'/blog/{blog}.tumblr.com/posts/{type}'
        valid_params = ['id', 'tag', 'limit', 'offset', 'reblog_info', 'notes_info', 'filter']

        response =  self.APIRequest('GET', req_url, params, valid_params)
        if raw:
            return response
        else:
            return json_parser(response, req_url, params)

    def avatar(self, blog, size=64, write=False, write_file=''):
        req_url = f'/blog/{blog}/avatar/{size}'

        avatar = self.APIRequest('GET-BINARY', req_url)

        if write:
            if not write_file:
                write_file = f'{blog}_{size}.png'
            with open(write_file, 'wb') as f:
                f.write(avatar)
        else:
            return avatar
