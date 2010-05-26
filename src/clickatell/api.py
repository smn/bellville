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
        """Enter the managed context, calling start() and storing
        the batch_id"""
        self.batch_id = self.start()
        return self
    
    def __exit__(self, *args, **kwargs):
        """Exit the managed context, calling end() with the batch_id"""
        self.end(self.batch_id)
    
    def sendmsg(self, context={}, **options):
        """
        Sending messages existing batches.
        
        Note: The fields 1-N that you defined in the template are used to 
              optionally personalise the message.
        """
        batch_id = options.get('batch_id', self.batch_id)
        if not batch_id:
            raise ClickatellError, "No batch_id set"
        
        options = validator.validate(options)
        options.update(context)
        options.update({
            'session_id': self.clickatell.session_id,
            'batch_id': batch_id,
        })
        [resp] = self.clickatell.client.batch('senditem', options)
        return resp
    
    def quicksend(self, **options):
        """
        Where one has the requirement to send the same message to multiple 
        recipients, you can use the quicksend command. This command offers 
        low overhead and maximum throughput. It is essentially a reference 
        to a predefined template and a string of destination addresses.
        
        Note: quicksend does not allow for templating
        """
        
        if 'context' in options:
            raise ClickatellError, 'context not allowed for quicksend()'
        
        batch_id = options.get('batch_id', self.batch_id)
        if not batch_id:
            raise ClickatellError, 'No batch_id set'
        options = validator.validate(options)
        options.update({
            'session_id': self.clickatell.session_id,
            'batch_id': batch_id,
            'to': validator.dispatch('to', options.pop('recipients'))
        })
        return self.clickatell.client.batch('quicksend', options)
    
    def start(self, options={}):
        """
        Once you have issued this command, you will be returned a batch ID 
        that is to be used when sending multiple batch items. Included 
        functionality also allows for message merging where you can substitute 
        fields that you have defined in your template. The field names are 
        called field1 though to fieldN.
        
        This command can take all the parameters of sendmsg, with the addition 
        of a template, and the exception of both the destination address and 
        the text fields. The template parameter must be URL encoded. It must 
        be used before either the senditem or quicksend command.
        """
        options.update(self.options)
        options.update({
            'session_id': self.clickatell.session_id
        })
        [resp] = self.clickatell.client.batch('startbatch', options)
        if isinstance(resp, IDResponse):
            return resp.value
        raise ClickatellError, resp
    
    def end(self, batch_id):
        """
        This command ends a batch and is not required (following a batch send). 
        Batches will expire automatically after 24 hours.
        """
        [resp] = self.clickatell.client.batch('endbatch', {
            'session_id': self.clickatell.session_id,
            'batch_id': batch_id
        })
        if isinstance(resp, OKResponse):
            return True
        raise ClickatellError, resp

class Clickatell(object):
    SESSION_TIME_OUT = timedelta(minutes=15)
    def __init__(self, username, password, api_id, client_class=Client,
                    sendmsg_defaults={}):
        self.username = username
        self.password = password
        self.api_id = api_id
        self.sendmsg_defaults = sendmsg_defaults
        self.client = client_class()
        self._session_start_time = None
    
    @property
    def session_id(self):
        """
        Returns a session id, used for authenticating against all of
        Clickatell's services.
        
        If the current session has expired, it'll reauthenticate and get
        a new session id. It'll return the current session id if it is 
        still valid.
        """
        if self.session_expired():
            self.session_id = self.get_new_session_id()
        return self._session_id
    
    @session_id.setter
    def session_id(self, session_token):
        """
        Sets the session token and resets the session time-out.
        """
        self.reset_session_timeout()
        self._session_id = session_token
        return self._session_id
    
    def reset_session_timeout(self):
        self._session_start_time = datetime.now()
    
    def get_new_session_id(self):
        """
        Get a new session id from Clickatell by authenticating with
        our username & password.
        
        Raises an error if there is an issue with the username and/or password
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
                    self.SESSION_TIME_OUT
    
    def ping(self):
        """
        Ping Clickatell to keep our session_id alive or raise an error if 
        something's wrong, e.g. the session_id has already expired.
        """
        [resp] = self.client.http('ping', {
            'session_id': self.session_id
        })
        if isinstance(resp, OKResponse):
            self.reset_session_timeout()
            return True
        raise ClickatellError, resp
    
    def sendmsg(self, **options):
        """
        send an SMS message. Accepts all the variables as documented by
        Clickatell in the HTTP api. Since `to` and `from` are keywords for 
        python they should be specified as 'sender' and 'recipients'. The
        recipients should be a list of MSISDNs.
        """
        options.update(self.sendmsg_defaults.copy())
        options = validator.validate(options)
        options.update({
            'to': validator.dispatch('to', options.pop('recipients')),
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
        [resp] = self.client.http('querymsg', kwargs)
        if isinstance(resp, IDResponse):
            return resp
        raise ClickatellError, resp
    
    def getbalance(self):
        """
        Returns the current balance as a float.
        """
        [resp] = self.client.http('getbalance', {
            'session_id': self.session_id
        })
        if isinstance(resp, CreditResponse):
            return resp.value
        raise ClickatellError, resp
    
    def check_coverage(self, msisdn):
        """
        Checks the available coverage for an MSISDN. It returns either an 
        OKResponse with the Charge specified in the extra dictionary or 
        an ERRResponse with the reason.
        """
        [resp] = self.client.utils('routeCoverage.php', {
            'msisdn': msisdn,
            'session_id': self.session_id
        })
        return resp
    
    def getmsgcharge(self, apimsgid):
        """
        Returns an ApiMsgIdResponse with the 'charge' and the 'status' in the
        extra dictionary or an ERRResponse with the error code and the reason
        """
        [resp] = self.client.http('getmsgcharge', {
            'session_id': self.session_id,
            'apimsgid': apimsgid
        })
        return resp
    
    def batch(self, **options):
        """
        Return a Batch messaging instance
        """
        options.update(self.sendmsg_defaults.copy())
        return Batch(self, validator.validate(options))
    