Bellville
=========

A Python Clickatell HTTP library.

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

If you're wanting to use the code then the following should be enough:

    $ python setup.py install

If you're looking to develop the code do the following:

    $ virtualenv --no-site-packages ve/
    $ source ve/bin/activate
    (ve)$ pip -E ve/ install -r requirements.pip
    (ve)$ python setup.py develop
    ...

The Clickatell library from `src/` will be on your PYTHONPATH and accessible via the Python shell.

Testing
=======

This project uses Nose for tests:

    (ve)$ nosetests
    ...

