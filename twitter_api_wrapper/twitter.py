import auth_settings
import oauth2
import json
import urlparse
import urllib


class Twitter_Exception(Exception):
    """Twitter Exception"""

    def __init__(self, reason):
        self.reason = unicode(reason)
        Exception.__init__(self, reason)

    def __str__(self):
        return self.reason


class Twitter_Rate_Limit_Exception(Twitter_Exception):
    """Twitter returned status code 429"""

    def __init__(self):
        self.reason = unicode('Exceed rate limit')
        Exception.__init__(self, self.reason)

    def __str__(self):
        return self.reason


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

        if status == 429:
            raise Twitter_Rate_Limit_Exception()

        if status != 200:
            message = '''Twitter responded with status %d, when trying to reach url %s

            %s''' \
                % (status, url, str(content))
            raise Twitter_Exception(message)

        if return_field:
            return content[return_field]

        return content

    def get_tweet(self, id):
        base_url = 'https://api.twitter.com/1.1/statuses/show.json'
        url = self.url_params(base_url, id=id)
        return self.request(url)