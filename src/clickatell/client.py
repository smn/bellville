import logging
from clickatell.http import HttpClient
from clickatell import response
from clickatell.errors import ClickatellError
from clickatell.utils import Dispatcher

class ResponseDispatcher(Dispatcher):
    
    def do_ok(self, *args, **kwargs):
        return response.OKResponse(*args)
    
    def do_err(self, *args, **kwargs):
        return response.ERRResponse(*args)
    
    def do_id(self, *args, **kwargs):
        return response.IDResponse(*args)
    
    def do_credit(self, *args, **kwargs):
        return response.CreditResponse(*args)
    
    def do_apimsgid(self, *args, **kwargs):
        return response.ApiMsgIdResponse(*args)
    
class Client(HttpClient):
    
    base_url = "https://api.clickatell.com"
    http_url = "%s/http" % base_url
    util_url = "%s/utils" % base_url
    
    def __init__(self):
        self.dispatcher = ResponseDispatcher()
    
    def process_response(self, data):
        return [self.dispatcher.dispatch(*response) for response in data]
    
    def do(self, command, kwargs={}):
        response = self.get('%s/%s' % (self.http_url, command), kwargs)
        logging.debug("Got response: %s" % response)
        return self.process_response(response)
