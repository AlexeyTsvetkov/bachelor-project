class Twitter_Exception(Exception):
    """Twitter Exception"""

    def __init__(self, reason, code, url):
        format = '''Twitter API responded with error code
        Status: %d
        Url: %s
        Reason: %s'''
        self.reason = format % (code, url, unicode(reason))
        self.code = code
        self.url = url
        Exception.__init__(self, reason)

    def __str__(self):
        return self.reason


class Twitter_Rate_Limit_Exception(Twitter_Exception):
    """Twitter returned status code 429"""

    def __init__(self, url):
        self.reason = 'Exceed rate limit'
        Exception.__init__(self, self.reason, 429, url)


class Twitter_Forbidden_Exception(Twitter_Exception):
    """Twitter returned status code 403"""

    def __init__(self, url):
        self.reason = 'Resource access is forbidden'
        Exception.__init__(self, self.reason, 403, url)


class Twitter_Not_Found_Exception(Twitter_Exception):
    """Twitter returned status code 404"""

    def __init__(self, url):
        self.reason = 'Resource not found'
        Exception.__init__(self, self.reason, 404, url)