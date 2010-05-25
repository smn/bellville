from datetime import datetime, timedelta
from clickatell import url
from clickatell.client import Client
from clickatell.response import OKResponse, ERRResponse, CreditResponse
from clickatell.errors import ClickatellError
from clickatell.validators import validate
from clickatell import constants as cc

class Clickatell(object):
    session_start_time = None
    session_time_out = timedelta(minutes=15)
    
    def __init__(self, username, password, api_id, client_class=Client, \
                    sendmsg_defaults={}):
        self.username = username
        self.password = password
        self.api_id = api_id
        self.sendmsg_defaults = sendmsg_defaults
        self.client = client_class()
    
    @property
    def session_id(self):
        if self.session_expired():
            self._session_id = self.get_new_session_id()
        return self._session_id
    
    def get_new_session_id(self):
        """
        Get a new session id from Clickatell by authenticating with
        our username & password.
        """
        [resp] = self.client.do('auth', {
            'user': self.username, 
            'password': self.password,
            'api_id': self.api_id
        })
        self.session_start_time = datetime.now()
        if isinstance(resp, OKResponse):
            return resp.value
        raise ClickatellError, resp
    
    def session_expired(self):
        """
        Return True or False depending on whether a session has expired
        or not. Calculated locally based on the time out value.
        """
        # If session_start_time hasn't been set then we do not have
        # a session yet
        if not self.session_start_time:
            return True
        return (datetime.now() - self.session_start_time) >= \
                    self.session_time_out
    
    def ping(self):
        """
        Ping Clickatell to keep our session_id alive
        """
        [resp] = self.client.do('ping', {
            'session_id': self.session_id
        })
        if isinstance(resp, OKResponse):
            return True
        else:
            raise ClickatellError, resp
    
    def sendmsg(self, **options):
        # clone the instance defaults
        options.update(self.sendmsg_defaults.copy())
        
        # timedeltas, validated to return minutes
        timedeltas = ['deliv_time', 'validity']
        for option in timedeltas:
            if option in options:
                options[option] = validate('timedelta', options.pop(option))
        
        # number, validated to ensure they are indeed numbers
        numbers = ['concat', 'max_credits', 'req_feat']
        for option in numbers:
            if option in options:
                options[option] = validate('number', options.pop(option))
        
        # timestamps, returned in Mysql timestamp format
        timestamps = ['scheduled_time']
        for option in timestamps:
            if option in options:
                options[option] = validate('timestamp', options.pop(option))
        
        # if from is specified then make sure something's been set as the
        # req_feat parameter as well.
        if 'sender' in options:
            options['from'] = validate('from', options.pop('sender'))
            if 'req_feat' not in options:
                raise ClickatellError, 'When specifying `sender` you also '\
                                        'need to specify the `req_feat` ' \
                                        'parameter'
        
        options.update({
            'to': ','.join(validate('to', options.pop('recipients'))),
            'text': validate('text', options.pop('text')),
            'session_id': self.session_id
        })
        return self.client.do('sendmsg', options)
    
    def querymsg(self,**kwargs):
        """
        This command returns the status of a message. You can query the status 
        with either the apimsgid or climsgid. The API Message ID (apimsgid) is 
        the message ID returned by the Gateway when a message has been 
        successfully submitted. If you specified your own unique client 
        message ID (climsgid) on submission, you may query the message status 
        using this value.
        """
        kwargs.update({'session_id': self.session_id})
        return self.client.do('querymsg', kwargs)
    
    def getbalance(self):
        [resp] = self.client.do('getbalance', {
            'session_id': self.session_id
        })
        if isinstance(resp, CreditResponse):
            return resp.value
        raise ClickatellError, resp
            