from datetime import datetime, timedelta
from clickatell import url

class Clickatell(object):
    
    url_opener = url.open
    session_start_time = None
    session_time_out = timedelta(minutes=15)

    def __init__(self, username, password, api_id):
        self.username = username
        self.password = password
        self.api_id = api_id
    
    @property
    def session_id(self):
        if not self.session_start_time:
            self.session_start_time = datetime.now()
    
    def session_expired(self):
        return (datetime.now() - self.session_start_time) >= \
                    self.session_time_out 
