Bellville, A Clickatell Python Library
======================================

A Python Clickatell HTTP library

::

    >>> from clickatell.api import Clickatell
    >>> from clickatell import constants as cc
    >>> clickatell = Clickatell('username','password','api_id', 
    ...                             sendmsg_defaults={
    ...                                    'callback': cc.YES,
    ...                                    'msg_type': cc.SMS_DEFAULT,
    ...                                    'deliv_ack': cc.YES,
    ...                                    'req_feat': cc.FEAT_ALPHA + \
    ...                                             cc.FEAT_NUMER + \
    ...                                             cc.FEAT_DELIVACK
    ...                              })
    >>> clickatell.sendmsg(recipients=['27123456789'], \
    ...                     sender='27123456789', text='hello world')
    [ERR: 301, No Credit Left]
    >>> 

Next steps, get some credit for your Clickatell account.


Getting started
===============

Make sure you have an account with Clickatell, they'll give you 10 free SMSs that you can use for testing. However, even undelivered messages count against your credit, make sure you use the library 100% correct if you're planning on actually using the 10. Use the username, password & api_id they provide.

If you're wanting to use the code then the following should be enough

::
    
    $ python setup.py install

If you're looking to develop the code do the following:

::
    
    $ virtualenv --no-site-packages ve/
    $ source ve/bin/activate
    (ve)$ pip -E ve/ install -r requirements.pip
    (ve)$ python setup.py develop
    ...

The Clickatell library from `src/` will be on your PYTHONPATH and accessible via the Python shell.

Testing
=======

This project uses Nose for tests, the `master` branch should be stable at all times:

::
    
    (ve)$ nosetests
    ...


Using Bellville
===============

Some code examples that illustrate how this thing works.

Sending a single SMS
--------------------

::
    
    >>> from clickatell.api import Clickatell
    >>> clickatell = Clickatell('username','password','api_id')
    >>> [resp] = clickatell.sendmsg(recipients=['27123456789'], 
    ...                                         sender='27123456789', 
    ...                                         text='hello world')
    >>> resp
    IDResponse: ce7f181a44a4a5b7e43fe2b9a0b1f0c1
    >>> resp.value # Clickatell's apiMsgId value
    'ce7f181a44a4a5b7e43fe2b9a0b1f0c1'
    >>> 
    
Sending an SMS to multiple recipients
-------------------------------------

::
    
    >>> [resp1, resp2] = clickatell.sendmsg(recipients=[
    ...                                         '27123456781',
    ...                                         '27123456782'], 
    ...                                     sender='27123456789',
    ...                                     text='hello world')
    >>> resp1.value # the apiMsgId
    'ce7f181a44a4a5b7e43fe2b9a0b1f0c1'
    >>> resp1.extra # the extra values returned for the response
    {'To': '27123456781'}
    >>> resp2.value
    'ce7f181a44a4a5b7e43fe2b9a0b1f0c2'
    >>> resp2.extra
    {'To': '27123456782'}
    >>>

Checking the status of a message
--------------------------------

Clickatell allows you to check the status of messages by polling their servers. However, they also allow you to use HTTP callbacks, where they post the status to your servers in realtime. **This is much faster and more efficient.** 

::
    
    >>> status = clickatell.querymsg( \
    ...                         apimsgid='ce7f181a44a4a5b7e43fe2b9a0b1f0c1')
    >>> status.value
    'ce7f181a44a4a5b7e43fe2b9a0b1f0c1'
    >>> status.extra
    {'Status': '002'}
    >>> 

Checking the balance of your Clickatell account
-----------------------------------------------

::
    
    >>> clickatell.getbalance()
    0.67000000000000004
    >>> 


Checking the coverage of an MSISDN
----------------------------------

::
    
    >>> clickatell.check_coverage('27219107700')
    ERRResponse: This prefix is not currently supported. Messages sent to this prefix will fail. Please contact support for assistance.
    >>> resp = clickatell.check_coverage('2776*******')
    >>> resp
    OKResponse: This prefix is currently supported. Messages sent to this prefix will be routed. Charge: 1
    >>> resp.value
    'This prefix is currently supported. Messages sent to this prefix will be routed.'
    >>> resp.extra
    {'Charge': '1'}
    >>> 
    
Checking the message charge
---------------------------

::
    
    >>> resp = clickatell.getmsgcharge( \
                                apimsgid='ce7f181a44a4a5b7e43fe2b9a0b1f0c1')
    >>> resp.value
    'ce7f181a44a4a5b7e43fe2b9a0b1f0c1'
    >>> resp.extra
    {'status': '002', 'charge': '1'}
    >>> 


Sending batches of messages
---------------------------

The responses from the `batch.sendmsg()` method are the same as from `clickatell.sendmsg()`.

::
    
    >>> batch = clickatell.batch(sender='27123456789', 
    ...                             template='Hello #field1# #field2#')
    >>> with batch:
    ...     batch.sendmsg(to='27123456781', context={
    ...         'field1': 'Foo 1', 
    ...         'field2':'Bar 1'
    ...     })
    ...     batch.sendmsg(to='27123456782', context={
    ...         'field1': 'Foo 2', 
    ...         'field2':'Bar 2'
    ...     })
    ... 
    ERRResponse: 301, No Credit Left
    ERRResponse: 301, No Credit Left
    >>> # shucks

For the `with` statement to work you'll need Python 2.6 or higher. It can work in Python 2.5 if you manually enable it with: 
    
    >>> from __future__ import with_statement

If you're not wanting to use the context manager you can manually call `batch.start()` and `batch.end()` with the `batch_id` argument.

::
    
    >>> batch = clickatell.batch(sender='27123456789', 
    ...                             template='Hello #field1# #field2#')
    >>> batch_id = batch.start()
    >>> batch.sendmsg(to='...', batch_id=batch_id, context={...})
    >>> batch.sendmsg(to='...', batch_id=batch_id, context={...})
    >>> batch.sendmsg(to='...', batch_id=batch_id, context={...})
    >>> batch.end(batch_id)


Sending a quick message to multiple recipients:
-----------------------------------------------

::
    
    >>> with clickatell.batch(sender='27123456789', 
    ...                         template='Hello world!') as batch:
    ...     [apimsgid1, apimsgid2, apimsgid3] = batch.quicksend(recipients=[
    ...         '27123456781',
    ...         '27123456782',
    ...         '27123456783',
    ...     ])
    ... 
    >>> apimsgid1
    ERRResponse: 301, No Credit Left To: 27123456781
    >>> apimsgid2
    ERRResponse: 301, No Credit Left To: 27123456782
    >>> apimsgid3
    ERRResponse: 301, No Credit Left To: 27123456783
    >>> 


Todo:
-----

Stuff that hasn't been implemented yet is:

    1. deletion of queued messages
    2. MMS push
    3. WAP push service indication
    4. Token voucher payment
    5. 8bit messaging
