from unittest import TestCase
from clickatell.api import Clickatell
from datetime import datetime, timedelta

class ClickatellTestCase(TestCase):
    
    def setUp(self):
        self.api = Clickatell("username", "password", "api_id")
    
    def tearDown(self):
        pass
    
    def test_client_creation(self):
        self.assertTrue(self.api)

    def test_session_timeout(self):
        delta = self.api.session_time_out
        self.api.session_start_time = datetime.now() - delta - \
                                                timedelta(minutes=1)
        self.assertTrue(self.api.session_expired())
    
class URLTestCase(TestCase):
    
    def test_get(self):
        from clickatell import url
        url.open('GET', 'http://www.google.com/search', {
            'q': 'Simon de Haan'
        })
    
    def test_post(self):
        from clickatell import url
        url.open('POST', 'http://www.google.com/search', {
            'q': 'Simon de Haan'
        })