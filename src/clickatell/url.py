import urllib
import urllib2
import logging
from clickatell.utils import Dispatcher

class URLDispatcher(Dispatcher):
    
    def do_post(self, url, data, headers):
        params = urllib.urlencode(data)
        request = urllib2.Request(url, data, headers)
        logging.debug('POST %s with %s' % (url, data))
        return request, urllib2.urlopen(request)

    def do_get(self, url, data, headers):
        params = urllib.urlencode(data)
        full_url = "%s?%s" % (url, params)
        logging.debug('GET %s' % full_url)
        request = urllib2.Request(full_url, None, headers)
        return request, urllib2.urlopen(request)
    

url_dispatcher = URLDispatcher()

def open(method, url, data={}, headers={}):
    return url_dispatcher.dispatch(method, url, data, headers)
