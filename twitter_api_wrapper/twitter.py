import auth_settings
import oauth2
import json
import urlparse
import urllib
from twitter_exceptions import *


class Twitter():
    """Twitter client wrapper"""

    def __init__(self):
        consumer = oauth2.Consumer(auth_settings.consumer_key, auth_settings.consumer_secret)
        token = oauth2.Token(auth_settings.app_key, auth_settings.app_secret)

        self.client = oauth2.Client(consumer, token=token)

    def url_params(self, base_url, **kwargs):
        url_parts = list(urlparse.urlparse(base_url))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(kwargs)

        url_parts[4] = urllib.urlencode(query)

        return urlparse.urlunparse(url_parts)

    def request(self, url, return_field=None):
        resp, content = self.client.request(url)
        content = json.loads(content)
        status = int(resp['status'])

        if status == 404:
            raise Twitter_Not_Found_Exception(url)

        if status == 429:
            raise Twitter_Rate_Limit_Exception(url)

        if status != 200:
            raise Twitter_Exception(str(content), status, url)

        if return_field:
            return content[return_field]

        return content

    def get_tweet(self, id):
        base_url = 'https://api.twitter.com/1.1/statuses/show.json'
        url = self.url_params(base_url, id=id)
        return self.request(url)