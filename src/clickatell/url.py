import urllib
import urllib2
from clickatell.errors import ClickatellError

class URLDispatcher(object):
    
    def do_post(self, url, data, headers):
        params = urllib.urlencode(data)
        f = urllib.urlopen(url, params)
        return f.read()

    def do_get(self, url, data, headers):
        params = urllib.urlencode(data)
        f = urllib.urlopen("%s?%s" % (url, params))
        return f.read()
    
    def dispatch(self, method, url, data = {}, headers = {}):
        method_name = 'do_%s' % method.lower()
        if hasattr(self, method_name):
            fn = getattr(self, method_name)
            return fn(url, data, headers)
        raise ClickatellError, 'No dispatcher available for %s' % method

url_dispatcher = URLDispatcher()

def open(method, url, data={}, headers={}):
    url_dispatcher.dispatch(method, url, data, headers)
