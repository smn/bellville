from unittest import TestCase
from clickatell.api import Clickatell
from clickatell.errors import ClickatellError
from clickatell.response import ERRResponse, OKResponse, ApiMsgIdResponse
from clickatell import constants as cc
from clickatell.tests.mock import TestClient
from datetime import datetime, timedelta

import logging
logging.basicConfig(level=logging.DEBUG)

base_url = "https://api.clickatell.com"
http_url = '%s/http' % base_url
utils_url = '%s/utils' % base_url
http_batch_url = '%s/http_batch' % base_url

auth_url = '%s/auth' % http_url
sendmsg_url = '%s/sendmsg' % http_url
querymsg_url = '%s/querymsg' % http_url
ping_url = '%s/ping' % http_url
getbalance_url = '%s/getbalance' % http_url
getmsgcharge_url = '%s/getmsgcharge' % http_url

check_coverage_url = '%s/routeCoverage.php' % utils_url

batch_start_url = '%s/startbatch' % http_batch_url
batch_send_url = '%s/senditem' % http_batch_url
quick_send_url = '%s/quicksend' % http_batch_url
batch_end_url = '%s/endbatch' % http_batch_url

sendmsg_defaults = {
    'callback': cc.CALLBACK_ALL,
    'deliv_ack': cc.YES,
    'req_feat': cc.FEAT_ALPHA + cc.FEAT_NUMER + cc.FEAT_DELIVACK,
    'msg_type': cc.SMS_DEFAULT,
}

def merge_with_defaults(d):
    tmp = {}
    tmp.update(sendmsg_defaults)
    tmp.update(d)
    return tmp

class ClickatellTestCase(TestCase):
    
    def setUp(self):
        self.username = 'username'
        self.password = 'password'
        self.api_id = '123456'
        self.clickatell = Clickatell(self.username, self.password, \
                                        self.api_id, client_class=TestClient,
                                        sendmsg_defaults=sendmsg_defaults)
        client = self.clickatell.client
        client.mock('GET', auth_url, {
            'user': self.username,
            'password': self.password,
            'api_id': self.api_id
        }, response=client.parse_content("OK: session_id_hash"))
    
    def test_sendmsg(self):
        client = self.clickatell.client
        client.mock('GET', sendmsg_url, merge_with_defaults({
            'session_id': 'session_id_hash',
            'to': '27123456789',
            'from': '27123456789',
            'text': 'hello world'
        }), response=client.parse_content("ID: apimsgid"))
        [id_] = self.clickatell.sendmsg(recipients=['27123456789'], 
                                        sender='27123456789', 
                                        text='hello world')
        self.assertEquals(id_.value, 'apimsgid')
    
    def test_sendmsg_multiple_recipients(self):
        client = self.clickatell.client
        client.mock('GET', sendmsg_url, merge_with_defaults({
            'session_id': 'session_id_hash',
            'to': '27123456781,27123456782',
            'from': '27123456789',
            'text': 'hello world'
        }), response=client.parse_content("ID: apimsgid To: 27123456781\n" 
                                            "ID: apimsgid To: 27123456782\n"))
        client.log_mocks()
        [id1, id2] = self.clickatell.sendmsg(recipients=[
                                            '27123456781',
                                            '27123456782'], 
                                        sender='27123456789', 
                                        text='hello world')
        self.assertEquals(id1.value, 'apimsgid')
        self.assertEquals(id1.extra, {'To': '27123456781'})
        self.assertEquals(id2.value, 'apimsgid')
        self.assertEquals(id2.extra, {'To': '27123456782'})
        self.assertTrue(client.all_mocks_called())
    
    def test_sendmsg_with_error(self):
        client = self.clickatell.client
        client.mock('GET', sendmsg_url, merge_with_defaults({
            'session_id': 'session_id_hash',
            'to': '27123456782',
            'from': '27123456782',
            'text': 'hello world'
        }), response=client.parse_content("ERR: 301, No Credit Left"))
        [err] = self.clickatell.sendmsg(recipients=['27123456782'],
                                            sender='27123456782',
                                            text='hello world')
        self.assertEquals(err.code, 301)
        self.assertEquals(err.reason, 'No Credit Left')
    
    def test_sendmsg_with_mixed_results(self):
        client = self.clickatell.client
        # first one will succeed, second will fail because credit ran out
        client.mock('GET', sendmsg_url, merge_with_defaults({
            'session_id': 'session_id_hash',
            'to': '27123456781,27123456782',
            'from': '27123456783',
            'text': 'hello world'
        }), response=client.parse_content("OK: apiMsgId To: 27123456781\n"
                                            "ERR: 301, No Credit Left\n"))
        [ok, err] = self.clickatell.sendmsg(recipients=[
                                                '27123456781',
                                                '27123456782'],
                                            sender='27123456783',
                                            text='hello world')
        self.assertEquals(ok.value, 'apiMsgId')
        self.assertEquals(ok.extra, {'To': '27123456781'})
        self.assertEquals(err.code, 301)
        self.assertEquals(err.reason, 'No Credit Left')
    
    def test_querymsg_with_apimsgid(self):
        clickatell = Clickatell('username', 'password', 'api_id', \
                                    client_class=TestClient,
                                    sendmsg_defaults=sendmsg_defaults)
        client = clickatell.client
        # first auth
        client.mock('GET', auth_url, {
            'user': 'username',
            'password': 'password',
            'api_id': 'api_id'
        }, response=client.parse_content('OK: sessionhash'))
        # then send msg
        client.mock('GET', sendmsg_url, merge_with_defaults({
            'session_id': 'sessionhash',
            'to': '27123456781',
            'from': '27123456781',
            'text': 'hello world'
        }), response=client.parse_content('ID: apiMsgId To: 27123456781'))
        # when checking the status respond with 002 - Message queued
        client.mock('GET', querymsg_url, {
            'session_id': 'sessionhash',
            'apimsgid': 'apiMsgId'
        }, response=client.parse_content('ID: apiMsgId Status: 002'))
        
        # run over the Mocked responses
        [send_response] = clickatell.sendmsg(recipients=['27123456781'],
                                                sender='27123456781',
                                                text='hello world')
        [status_response] = clickatell.querymsg(apimsgid=send_response.value)
        
        # check the mocked session hash
        self.assertEquals(clickatell.session_id, 'sessionhash')
        # check the mocked sendmsg responses
        self.assertEquals(send_response.value, 'apiMsgId')
        self.assertEquals(send_response.extra['To'], '27123456781')
        # check the mocked querymsg responses
        self.assertEquals(status_response.value, 'apiMsgId')
        self.assertEquals(status_response.extra['Status'], '002')
    
    def test_sendmsg_recipient_validation(self):
        clickatell = Clickatell('username','password','api_id', 
                                    client_class=TestClient,
                                    sendmsg_defaults=sendmsg_defaults)
        clickatell.session_id = "session_id"
        self.assertFalse(clickatell.session_expired())
        for recipient in ['+27123456781', '0027123456781']:
            kwargs = {
                'sender': '27123456781',
                'recipients': [recipient],
                'text': 'hello world'
            }
            self.assertRaises(ClickatellError, clickatell.sendmsg, **kwargs)
    
    def test_getbalance(self):
        clickatell = Clickatell('username', 'password', 'api_id', 
                                    client_class=TestClient)
        clickatell.session_id = "session_id"
        self.assertFalse(clickatell.session_expired())
        clickatell.client.mock('GET', getbalance_url, {
            'session_id': 'session_id'
        }, response=clickatell.client.parse_content('Credit: 500.00'))
        self.assertEquals(clickatell.getbalance(), 500.00)
    
    def test_getbalance_fail(self):
        clickatell = Clickatell('username', 'password', 'api_id', 
                                    client_class=TestClient)
        clickatell.session_id = 'session_id'
        clickatell.client.mock('GET', getbalance_url, {
            'session_id': 'session_id'
        }, response=clickatell.client.parse_content('ERR: 003, Session ID Expired'))
        self.assertRaises(ClickatellError, clickatell.getbalance)
    
    def test_check_coverage(self):
        clickatell = Clickatell('username', 'password', 'api_id',
                                    client_class=TestClient)
        clickatell.session_id = "session_id"
        clickatell.client.mock('GET', check_coverage_url, {
            'session_id': clickatell.session_id,
            'msisdn': '27123456781'
        }, response=clickatell.client.parse_content(
                'OK:  This prefix is currently supported. Messages sent to ' \
                'this prefix will be routed. Charge: 1'
        ))
        
        resp = clickatell.check_coverage(msisdn='27123456781')
        self.assertTrue(isinstance(resp, OKResponse))
        self.assertEquals(resp.value, 'This prefix is currently supported. '\
                                        'Messages sent to this prefix will '\
                                        'be routed.')
        self.assertEquals(resp.extra['Charge'], '1')
    
    def test_check_coverage_fail(self):
        clickatell = Clickatell('username', 'password', 'api_id',
                                    client_class=TestClient)
        clickatell.session_id = "session_id"
        clickatell.client.mock('GET', check_coverage_url, {
            'session_id': clickatell.session_id,
            'msisdn': '27123456781'
        }, response=clickatell.client.parse_content(
            'ERR: This prefix is not currently supported. Messages sent to '\
            'this prefix will fail. Please contact support for assistance.'
        ))
        
        resp = clickatell.check_coverage(msisdn='27123456781')
        self.assertTrue(isinstance(resp, ERRResponse))
        self.assertEquals(resp.value, 
            'This prefix is not currently supported. Messages sent to this '\
            'prefix will fail. Please contact support for assistance.')
    
    def test_getmsgcharge(self):
        clickatell = Clickatell('username', 'password', 'api_id',
                                    client_class=TestClient)
        clickatell.session_id = "session_id"
        clickatell.client.mock('GET', getmsgcharge_url, {
            'session_id': clickatell.session_id,
            'apimsgid': 'apimsgid'
        }, response=clickatell.client.parse_content(
            'apiMsgId: apimsgid charge: 1 status: 002'
        ))
        
        resp = clickatell.getmsgcharge(apimsgid='apimsgid')
        self.assertTrue(isinstance(resp, ApiMsgIdResponse))
        self.assertEquals(resp.value, 'apimsgid')
        self.assertEquals(resp.extra, {'charge': '1', 'status': '002'})
    
    def test_getmsgcharge_fail(self):
        clickatell = Clickatell('username', 'password', 'api_id',
                                    client_class=TestClient)
        clickatell.session_id = "session_id"
        clickatell.client.mock('GET', getmsgcharge_url, {
            'session_id': clickatell.session_id,
            'apimsgid': 'apimsgid'
        }, response=clickatell.client.parse_content(
            'ERR: 108, Invalid or missing API ID'
        ))
        
        resp = clickatell.getmsgcharge(apimsgid='apimsgid')
        self.assertTrue(isinstance(resp, ERRResponse))
        self.assertEquals(resp.code, 108)
        self.assertEquals(resp.reason, 'Invalid or missing API ID')
    
    def _setup_clickatell_for_batch_test(self):
        clickatell = Clickatell('username', 'password', 'api_id', 
                                    client_class=TestClient, 
                                    sendmsg_defaults=sendmsg_defaults)
        clickatell.session_id = 'session_id'
        client = clickatell.client
        # it should start the batch
        client.mock('GET', batch_start_url, merge_with_defaults({
            'session_id': clickatell.session_id,
            'template': 'Hello #name# #surname#',
            'from': '27123456789'
        }), response=client.parse_content('ID: batch_id'))
        # it should send two messages via the batch
        client.mock('GET', batch_send_url, {
            'session_id': clickatell.session_id,
            'batch_id': 'batch_id',
            'to': '27123456781',
            'name': 'Foo 1',
            'surname': 'Bar 1'
        }, response=client.parse_content('ID: apimsgid1'))
        client.mock('GET', batch_send_url, {
            'session_id': clickatell.session_id,
            'batch_id': 'batch_id',
            'to': '27123456782',
            'name': 'Foo 2',
            'surname': 'Bar 2'
        }, response=client.parse_content('ID: apimsgid2'))
        # it should end the batch
        client.mock('GET', batch_end_url, {
            'session_id': clickatell.session_id,
            'batch_id': 'batch_id'
        }, response=client.parse_content('OK'))
        return clickatell
    
    def test_batch_send_with_context_manager(self):
        clickatell = self._setup_clickatell_for_batch_test()
        batch = clickatell.batch(sender='27123456789', 
                                    template='Hello #name# #surname#')
        with batch:
            batch.sendmsg(to='27123456781', context={
                'name': 'Foo 1', 
                'surname':'Bar 1'
            })
            batch.sendmsg(to='27123456782', context={
                'name': 'Foo 2', 
                'surname':'Bar 2'
            })
        self.assertTrue(clickatell.client.all_mocks_called())
    
    def test_batch_send_without_context_manager(self):
        clickatell = self._setup_clickatell_for_batch_test()
        batch = clickatell.batch(sender='27123456789',
                                    template='Hello #name# #surname#')
        batch_id = batch.start()
        batch.sendmsg(to='27123456781', batch_id=batch_id, context={
            'name': 'Foo 1', 
            'surname':'Bar 1'
        })
        batch.sendmsg(to='27123456782', batch_id=batch_id, context={
            'name': 'Foo 2', 
            'surname':'Bar 2'
        })
        batch.end(batch_id)
        self.assertTrue(clickatell.client.all_mocks_called())
    
class SessionTestCase(TestCase):
    def test_session_timeout(self):
        """
        Check the session time out check by forcing the timeout
        one minute past the allowed limit
        """
        clickatell = Clickatell("username", "password", "api_id", \
                                client_class=TestClient,
                                sendmsg_defaults=sendmsg_defaults)
        delta = clickatell.session_time_out
        clickatell._session_start_time = datetime.now() - delta - \
                                                timedelta(minutes=1)
        self.assertTrue(clickatell.session_expired())
    
    def test_ping(self):
        """
        Pinging resets the session timeout delay
        """
        clickatell = Clickatell('username', 'password', 'api_id', \
                                    client_class=TestClient,
                                    sendmsg_defaults=sendmsg_defaults)
        client = clickatell.client
        client.mock('GET', auth_url, {
            'user': 'username',
            'password': 'password',
            'api_id': 'api_id'
        }, response=client.parse_content("OK: somerandomhash"))
        client.mock('GET', ping_url, {
            'session_id': 'somerandomhash'
        }, response=client.parse_content("OK: "))
        self.assertTrue(clickatell.ping())
        self.assertTrue(client.all_mocks_called())
    
    def test_ping_error(self):
        """
        Pinging can raise an error for an invalid session_id
        """
        clickatell = Clickatell('username', 'password', 'api_id', \
                                    client_class=TestClient,
                                    sendmsg_defaults=sendmsg_defaults)
        client = clickatell.client
        client.mock('GET', auth_url, {
            'user': 'username',
            'password': 'password',
            'api_id': 'api_id'
        }, response=client.parse_content('OK: somerandomhash'))
        # when we ping return an error value as if the hash is now invalid
        client.mock('GET', ping_url, {
            'session_id': 'somerandomhash'
        }, response=client.parse_content('ERR: 003, Session ID Expired'))
        self.assertRaises(ClickatellError, clickatell.ping)
        self.assertTrue(client.all_mocks_called())
    
    def test_reauthentication_on_session_timeout(self):
        """
        If the session_id property is called when the session has actually 
        timed out it should need to reauthenticate and get new a new session_id
        """
        clickatell = Clickatell("username", "password", "api_id", \
                                    client_class=TestClient,
                                    sendmsg_defaults=sendmsg_defaults)
        # manually set it for comparison later
        clickatell.session_id = "old_session_hash"
        self.assertEquals(clickatell.session_id, 'old_session_hash')
        # manually expire by setting the session_start_time beyond the allowed
        # timeout
        clickatell._session_start_time = datetime.now() - \
                                            (clickatell.session_time_out * 2)
        # next api.session_id call should call the auth url 
        # because the session's timed out
        clickatell.client.mock('GET', auth_url, {
            'user': 'username',
            'password': 'password',
            'api_id': 'api_id'
        }, response=clickatell.client.parse_content('OK: new_session_hash'))
        self.assertEquals(clickatell.session_id, 'new_session_hash')
        # make sure the URLs we expected to be called all actually did
        self.assertTrue(clickatell.client.all_mocks_called())

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
        [ok] = client.http('auth', {
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
        [err] = client.http('auth', {
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

