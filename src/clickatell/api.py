from datetime import datetime, timedelta
from contextlib import contextmanager

from clickatell import url
from clickatell.client import Client
from clickatell.response import OKResponse, ERRResponse, CreditResponse, IDResponse
from clickatell.errors import ClickatellError
from clickatell.validators import validator
from clickatell import constants as cc

class Batch(object):
    def __init__(self, clickatell, options):
        self.clickatell = clickatell
        self.options = options
        self.batch_id = None
    
    def __enter__(self, *args, **kwargs):
        self.batch_id = self.start()
    
    def __exit__(self, *args, **kwargs):
        self.end(self.batch_id)
    
    def sendmsg(self, context={}, **options):
        self.batch_id = options.get('batch_id') or self.batch_id
        if not self.batch_id:
            raise ClickatellError, "Call start() before send()"
        
        options = validator.validate(options)
        options.update(context)
        options.update({
            'session_id': self.clickatell.session_id,
            'batch_id': self.batch_id,
        })
        [resp] = self.clickatell.client.batch('senditem', options)
        return resp
    
    def start(self):
        options = self.options.copy()
        options.update({
            'session_id': self.clickatell.session_id
        })
        [resp] = self.clickatell.client.batch('startbatch', options)
        if isinstance(resp, IDResponse):
            return resp.value
        raise ClickatellError, resp
    
    def end(self, batch_id):
        [resp] = self.clickatell.client.batch('endbatch', {
            'session_id': self.clickatell.session_id,
            'batch_id': batch_id
        })
        if isinstance(resp, OKResponse):
            return True
        raise ClickatellError, resp

class Clickatell(object):
    _session_start_time = None
    session_time_out = timedelta(minutes=15)
    
    def __init__(self, username, password, api_id, client_class=Client,
                    sendmsg_defaults={}):
        self.username = username
        self.password = password
        self.api_id = api_id
        self.sendmsg_defaults = sendmsg_defaults
        self.client = client_class()
    
    @property
    def session_id(self):
        if self.session_expired():
            self.session_id = self.get_new_session_id()
        return self._session_id
    
    @session_id.setter
    def session_id(self, session_token):
        self.reset_session_timeout()
        self._session_id = session_token
        return self._session_id
    
    def reset_session_timeout(self):
        self._session_start_time = datetime.now()
    
    def get_new_session_id(self):
        """
        Get a new session id from Clickatell by authenticating with
        our username & password.
        """
        [resp] = self.client.http('auth', {
            'user': self.username, 
            'password': self.password,
            'api_id': self.api_id
        })
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
        if not self._session_start_time:
            return True
        return (datetime.now() - self._session_start_time) >= \
                    self.session_time_out
    
    def ping(self):
        """
        Ping Clickatell to keep our session_id alive
        """
        [resp] = self.client.http('ping', {
            'session_id': self.session_id
        })
        if isinstance(resp, OKResponse):
            self.reset_session_timeout()
            return True
        else:
            raise ClickatellError, resp
    
    def sendmsg(self, **options):
        # clone the instance defaults
        options.update(self.sendmsg_defaults.copy())
        options = validator.validate(options)
        options.update({
            'to': ','.join(validator.dispatch('to', options.pop('recipients'))),
            'text': validator.dispatch('text', options.pop('text')),
            'session_id': self.session_id
        })
        return self.client.http('sendmsg', options)
    
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
        return self.client.http('querymsg', kwargs)
    
    def getbalance(self):
        [resp] = self.client.http('getbalance', {
            'session_id': self.session_id
        })
        if isinstance(resp, CreditResponse):
            return resp.value
        raise ClickatellError, resp
    
    def check_coverage(self, msisdn):
        [resp] = self.client.utils('routeCoverage.php', {
            'msisdn': msisdn,
            'session_id': self.session_id
        })
        return resp
    
    def getmsgcharge(self, apimsgid):
        [resp] = self.client.http('getmsgcharge', {
            'session_id': self.session_id,
            'apimsgid': apimsgid
        })
        return resp
    
    def batch(self, **options):
        options.update(self.sendmsg_defaults.copy())
        return Batch(self, validator.validate(options))
    