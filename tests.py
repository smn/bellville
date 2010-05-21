from unittest import TestCase
from clickatell.api import Clickatell
from clickatell.errors import ClickatellError
from clickatell.response import ERRResponse, OKResponse
from clickatell.tests.mock import TestClient
from datetime import datetime, timedelta

base_url = "https://api.clickatell.com/http"
auth_url = '%s/auth' % base_url
sendmsg_url = '%s/sendmsg' % base_url
ping_url = '%s/ping' % base_url

class ClickatellTestCase(TestCase):
    
    def setUp(self):
        self.username = 'username'
        self.password = 'password'
        self.api_id = '123456'
        self.clickatell = Clickatell(self.username, self.password, \
                                        self.api_id, client_class=TestClient)
        client = self.clickatell.client
        client.mock('GET', auth_url, {
            'user': self.username,
            'password': self.password,
            'api_id': self.api_id
        }, response=client.parse_content("OK: session_id_hash"))
    
    def test_sendmsg(self):
        client = self.clickatell.client
        client.mock('GET', sendmsg_url, {
            'session_id': 'session_id_hash',
            'to': '27123456789',
            'from': '27123456789',
            'text': 'hello world'
        }, response=client.parse_content("ID: apimsgid"))
        client.log_mocks()
        [id_] = self.clickatell.sendmsg(recipient='27123456789', 
                                        sender='27123456789', 
                                        text='hello world')
        self.assertTrue(id_.value, 'apimsgid')
    
    def test_sendmsg_multiple_recipients(self):
        client = self.clickatell.client
        client.mock('GET', sendmsg_url, {
            'session_id': 'session_id_hash',
            'to': '27123456781,27123456782',
            'from': '27123456789',
            'text': 'hello world'
        }, response=client.parse_content("""ID: apimsgid To: 27123456781
ID: apimsgid To: 27123456782
"""))
        client.log_mocks()
        [id1, id2] = self.clickatell.sendmsg(recipients=[
                                            '27123456781',
                                            '27123456782'], 
                                        sender='27123456789', 
                                        text='hello world')
        self.assertTrue(id1.value, 'apimsgid')
        self.assertTrue(id1.extra, {'To': '27123456781'})
        self.assertTrue(id2.value, 'apimsgid')
        self.assertTrue(id2.extra, {'To': '27123456782'})
    
class SessionTestCase(TestCase):
    def test_session_timeout(self):
        """
        Check the session time out check by forcing the timeout
        one minute past the allowed limit
        """
        clickatell = Clickatell("username", "password", "api_id", \
                                client_class=TestClient)
        delta = clickatell.session_time_out
        clickatell.session_start_time = datetime.now() - delta - \
                                                timedelta(minutes=1)
        self.assertTrue(clickatell.session_expired())

class AuthenticationTestCase(TestCase):
    """Test authentication schemes"""
    def test_ok_authentication(self):
        "test OK / success response"
        client = TestClient()
        client.mock('get', auth_url, {
            'user': 'username',
            'password': 'password',
            'api_id': '123456'
        }, response=client.parse_content("OK: somerandomhash"))
        [ok] = client.do('auth', {
            'user': 'username', 
            'password': 'password', 
            'api_id': '123456'
        })
        self.assertTrue(isinstance(ok, OKResponse))
        self.assertEquals(ok.value, 'somerandomhash')
    
    def test_err_authentication(self):
        "test ERR / fail response"
        client = TestClient()
        client.mock('get', auth_url, {
            'user': 'username',
            'password': 'password',
            'api_id': '123456'
        }, response=client.parse_content('ERR: 001, Authentication Failed'))
        [err] = client.do('auth', {
            'user': 'username', 
            'password': 'password', 
            'api_id': '123456'
        })
        self.assertTrue(isinstance(err, ERRResponse))
        self.assertEquals(err.code, 1)
        self.assertEquals(err.reason, 'Authentication Failed')

class ResponseTestCase(TestCase):
    """Test parsing of response values into Response objects"""
    def test_ok_response(self):
        """OK should split the result string into a list based on spaces"""
        ok = OKResponse("a" * 32)
        self.assertEquals(ok.value, "a" * 32)
        self.assertEquals(ok.extra, {})
    
    def test_ok_response_with_spaces(self):
        ok = OKResponse("a b c d e")
        self.assertEquals(ok.value, 'a b c d e')
        self.assertEquals(ok.extra, {})
    
    def test_err_response(self):
        """ERRReponse should provide a code and a reason if available"""
        err = ERRResponse("001, Authentication Failed")
        self.assertEquals(err.code, 1)
        self.assertEquals(err.reason, "Authentication Failed")
        
        err = ERRResponse("007")
        self.assertEquals(err.code, 7)
        self.assertEquals(err.reason, '')
    
    def test_parsing_of_response(self):
        resp = OKResponse("apiMsgId To: 27123456782")
        self.assertEquals(resp.value, 'apiMsgId')
        self.assertEquals(resp.extra, {'To':'27123456782'})

class MockingTestCase(TestCase):
    """
    Tests to make sure the mocking code we're using in the other tests
    is actually working properly.
    """
    
    def test_get(self):
        client = TestClient()
        mocked_response = {'OK': '123456789'}
        data = {'q': "Testing Client Lib"}
        client.mock('GET', 'http://api.clickatell.com', \
                                data = data, response = mocked_response)
        self.assertEquals(mocked_response, \
                            client.get('http://api.clickatell.com', \
                                                data=data))
    
    def test_post(self):
        client = TestClient()
        mocked_response = {'OK': '123456789'}
        data = {'keyword': 'argument'}
        client.mock('POST', 'http://api.clickatell.com', \
                                data=data, response=mocked_response)
        self.assertEquals(mocked_response, \
                            client.post('http://api.clickatell.com', \
                                                data=data))

