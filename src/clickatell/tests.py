from unittest import TestCase
from clickatell.api import Clickatell

class ClickatellTestCase(TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_client_creation(self):
        api = Clickatell("username", "password", "api_id")
        self.assertTrue(api) 
