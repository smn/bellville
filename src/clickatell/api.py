from datetime import datetime, timedelta
from clickatell import url
from clickatell.client import Client

class Clickatell(object):
    session_start_time = None
    session_time_out = timedelta(minutes=15)

    def __init__(self, username, password, api_id, client_class=Client):
        self.username = username
        self.password = password
        self.api_id = api_id
        self.client = client_class()
    
    @property
    def session_id(self):
        if session_expired():
            self._session_id = self.get_new_session_id()
        return self._session_id
    
    def get_new_session_id(self):
        """
        Get a new session id from Clickatell by authenticating with
        our username & password.
        """
        self.client.do('auth', {
            'user': self.username, 
            'pass': self.password,
            'api_id': self.api_id
        })
    
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
