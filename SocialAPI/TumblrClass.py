from .APIBase import APIBase

class Tumblr(APIBase):
    api_url = 'https://api.tumblr.com/'
    tokenurl_request = 'http://www.tumblr.com/oauth/request_token'
    tokenurl_authorize = 'http://www.tumblr.com/oauth/authorize'
    tokenurl_access = 'http://www.tumblr.com/oauth/access_token'
    oauthv = 1

    def get_tokens(self, save, quiet, file='tumblr.conf.json'):
        self.api_tokens(save, quiet, file)

    def info(self, blog=''):
        if blog:
            req_url = f'/v2/blog/{blog}.tumblr.com/info'
        else:
            req_url = '/v2/user/info'

        return self.api_request('GET', req_url)

    def likes(self, blog='', **params):
        if blog:
            req_url = f'/v2/blog/{blog}.tumblr.com/likes'
        else:
            req_url = '/v2/user/likes'
        valid_params = ['limit', 'offset', 'before', 'after']

        return self.api_request('GET', req_url, params, valid_params)

    def following(self, blog='', **params):
        if blog:
            req_url = f'/v2/blog/{blog}.tumblr.com/following'
        else:
            req_url = '/v2/user/following'
        valid_params = ['limit', 'offset']

        return self.api_request('GET', req_url, params, valid_params)

    def dashboard(self, **params):
        req_url = '/v2/user/dashboard'
        valid_params = ['limit', 'offset', 'type', 'since_id', 'reblog_info', 'notes_info']

        return self.api_request('GET', req_url, params, valid_params)

    def posts(self, blog, type='', **params):
        req_url = f'/v2/blog/{blog}.tumblr.com/posts/{type}'
        valid_params = ['id', 'tag', 'limit', 'offset', 'reblog_info', 'notes_info', 'filter']

        return self.api_request('GET', req_url, params, valid_params)

    def avatar(self, blog, size=64, write=False, write_file=''):
        req_url = f'/v2/blog/{blog}/avatar/{size}'

        avatar = self.api_request('GET-BINARY', req_url)

        if write:
            if not write_file:
                write_file = f'{blog}_{size}.png'
            with open(write_file, 'wb') as f:
                f.write(avatar)
        else:
            return avatar
