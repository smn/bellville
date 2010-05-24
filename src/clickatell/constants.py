"""
Final or intermediary statuses are passed back by the API depending on the 
callback value set in the original post. The callback URL and optional 
"Username" and "Password" authentication parameters can be set in the 
preferences section of the particular API product within your client account, 
after logging in online. The URL must begin with either http:// (non-encrypted) 
or https:// (encrypted). These are NOT your Clickatell username and password 
but are a username and password of your choice to add additional security.
The variables returned are apiMsgId, cliMsgId, to, timestamp, from, 
status and charge.
"""
CALLBACK_NONE = 0
CALLBACK_INTERMEDIATE = 1
CALLBACK_FINAL = 2
CALLBACK_ALL = 3


"""
Boolean types
"""
NO = 0
YES = 1


"""
This parameter specifies the features that must be present in order for 
message delivery to occur. If all features are not present, the message will 
not be delivered. This prevents SMS messages arriving at a destination via 
the least-cost gateway, without certain features. This would, for instance, 
prevent the dropping of an sender ID. This means that we will not route 
messages through a gateway that cannot support the required features you have 
set. For certain message types, we always set the required feature bitmask 
where relevant. These are FEAT_8BIT, FEAT_UDH, FEAT_UCS2 and FEAT_CONCAT.

This parameter is set using a combined decimal number to refer to the 
additional required features.

E.g.: 32 + 512 = 544 - Numeric sender ID and Flash SMS both required. 
The value you would set to ensure that Flash and numeric sender ID are both 
supported, would therefore be 544. To ensure that delivery acknowledgment and 
alphanumeric IDs are supported you would use the value 8240 (16 + 32 + 8192).
"""
FEAT_TEXT = 1
FEAT_8BIT = 2
FEAT_UDH = 4
FEAT_UCS2 = 8
FEAT_ALPHA = 16
FEAT_NUMER = 32
FEAT_FLASH = 512
FEAT_DELIVACK = 8192
FEAT_CONCAT = 16384

"""
Setting this parameter will assign the message to one of three queues assigned 
to each user account. This sets the priority of a message sent to us, relative 
to other messages sent from the same user account. Messages in queue number 1, 
will always be delivered before messages in queue number 2 and 3, while 
messages in the 3rd queue, will have the lowest priority (relative to queues 1 
and 2).

This is useful when delivering, for example, a single high priority message 
while you have a large batch going through that same account. The large batch 
will be queued through queue number 3 (default), and urgent alerts (sent 
through queue 1), will be delivered ahead of those messages in the batch 
(queue 3), regardless of when they are actually sent to us.
"""

QUEUE_HIGH = 1
QUEUE_MEDIUM = 2
QUEUE_LOW = 3

"""
A wide variety of messages can be sent through our gateway. We have pre-defined 
a number of SMS message-types in the API, so that you do not have to set the 
UDH (user data header) manually.
"""

SMS_TEXT = "SMS_TEXT"
SMS_FLASH = "SMS_FLASH"
SMS_NOKIA_OLOGO = "SMS_NOKIA_OLOGO"
SMS_NOKIA_GLOGO = "SMS_NOKIA_GLOGO"
SMS_NOKIA_PICTURE = "SMS_NOKIA_PICTURE"
SMS_NOKIA_RINGTONE = "SMS_NOKIA_RINGTONE"
SMS_NOKIA_RTTL = "SMS_NOKIA_RTTL"
SMS_NOKIA_CLEAN = "SMS_NOKIA_CLEAN"
SMS_NOKIA_VCARD = "SMS_NOKIA_VCARD"
SMS_NOKIA_VCAL = "SMS_NOKIA_VCAL"
SMS_DEFAULT = SMS_TEXT