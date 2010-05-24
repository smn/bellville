from clickatell.utils import Dispatcher
from clickatell.errors import ClickatellError

class SendMsgValidator(Dispatcher):
    
    def do_to(self, recipients):
        if any([recipient.startswith('+') or recipient.startswith('0')
                for recipient in recipients]):
            raise ClickatellError, "SMS messages need to be sent in the " \
                                    "standard international format, with " \
                                    "country code followed by number. No " \
                                    "leading zero to the number and no " \
                                    "special characters such as '+' or " \
                                    "spaces must be used."
        return recipients
    
    def do_from(self, _from):
        if _from.isdigit() and len(_from) <= 16:
            return _from
        elif _from.isalpha() and len(_from) <= 11:
            return _from
        raise ClickatellError, "The source address (from), also known as the " \
                                "sender ID, can be either a valid international " \
                                "format number between 1 and 16 characters " \
                                "long, or an 11 character alphanumeric string."
    def do_text(self, text):
        return text

send_msg_validator = SendMsgValidator()