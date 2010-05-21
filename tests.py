from unittest import TestCase
from clickatell.api import Clickatell
from clickatell.errors import ClickatellError
from clickatell.http import HttpClient
from clickatell.client import Client, ERRResponse, OKResponse
from datetime import datetime, timedelta

import logging
logging.basicConfig(level=logging.DEBUG)

base_url = "https://api.clickatell.com/http"

class TestHttpClient(HttpClient):
    """A Client that allows us to mock the expected response"""
    queue = {}
    
    def mock(self, method, url, data={}, headers={}, response={}):
        method = method.upper()
        self.queue.setdefault(method, [])
        self.queue[method].append((url, data, headers, response))
    
    def get_mocked(self, method, url, data={}, headers={}):
        method = method.upper()
        method_queue = self.queue.get(method, [])
        for s_url, s_data, s_headers, response in method_queue:
            if (url == s_url) \
                and (data == s_data) \
                and (headers == s_headers):
                logging.debug("Mocked response: %s" % response)
                return response
        raise ClickatellError, 'No matching mocked data'
    
    def get(self, *args, **kwargs):
        return self.get_mocked('get', *args, **kwargs)
    
    def post(self, *args, **kwargs):
        return self.get_mocked('post', *args, **kwargs)
    

class TestClient(Client, TestHttpClient):
    pass

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

class ClickatellClientTestCase(TestCase):
    
    def test_authentication(self):
        client = TestClient()
        client.mock('get', '%s/%s' % (base_url, 'auth'), {
            'user': 'username',
            'password': 'password',
            'api_id': '123456'
        }, response=client.parse_content("OK: somerandomhash"))
        [ok] = client.do('auth', user='username', password='password', \
                    api_id='123456')
        self.assertEquals(ok.results, ['somerandomhash'])

class ClickatellResponseTestCase(object):
    
    def test_ok_response(self):
        ok = OKResponse("a" * 32)
        self.assertEquals(ok.results, ["*" * 32])
    
    def test_err_response(self):
        err = ERRResponse("001, Authentication Failed")
        self.assertEquals(err.code, 1)
        self.assertEquals(err.reason, "Authentication Failed")

class URLTestCase(TestCase):
    
    def setUp(self):
        self.client = TestClient()
    
    def test_get(self):
        mocked_response = {'OK': '123456789'}
        data = {'q': "Testing Client Lib"}
        self.client.mock('GET', 'http://api.clickatell.com', \
                                data = data, response = mocked_response)
        self.assertEquals(mocked_response, \
                            self.client.get('http://api.clickatell.com', \
                                                data=data))
    
    def test_post(self):
        mocked_response = {'OK': '123456789'}
        data = {'keyword': 'argument'}
        self.client.mock('POST', 'http://api.clickatell.com', \
                                data=data, response=mocked_response)
        self.assertEquals(mocked_response, \
                            self.client.post('http://api.clickatell.com', \
                                                data=data))

