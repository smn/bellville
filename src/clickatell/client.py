import logging
from clickatell.http import HttpClient
from clickatell.response import OKResponse, ERRResponse
from clickatell.errors import ClickatellError
from clickatell.utils import Dispatcher

class ResponseDispatcher(Dispatcher):
    
    def do_ok(self, *args, **kwargs):
        return OKResponse(*args)
    
    def do_err(self, *args, **kwargs):
        return ERRResponse(*args)
    
class Client(HttpClient):
    
    base_url = "https://api.clickatell.com/http"
    
    def __init__(self):
        self.dispatcher = ResponseDispatcher()
    
    def process_reponse(self, data):
        return [self.dispatcher.dispatch(*response) for response in data]
    
    def do(self, command, **kwargs):
        response = self.get('%s/%s' % (self.base_url, command), kwargs)
        logging.debug("Got response: %s" % response)
        return self.process_reponse(response)
    
