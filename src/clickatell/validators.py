from clickatell.utils import Dispatcher
from clickatell.errors import ClickatellError
from datetime import datetime, timedelta

class Validator(Dispatcher):
    
    def validate_to(self, recipients):
        if any([recipient.startswith('+') or recipient.startswith('0')
                for recipient in recipients]):
            raise ClickatellError, "SMS messages need to be sent in the " \
                                    "standard international format, with " \
                                    "country code followed by number. No " \
                                    "leading zero to the number and no " \
                                    "special characters such as '+' or " \
                                    "spaces must be used."
        return recipients
    
    def validate_from(self, _from):
        if _from.isdigit() and len(_from) <= 16:
            return _from
        elif _from.isalpha() and len(_from) <= 11:
            return _from
        raise ClickatellError, "The source address (from), also known as the " \
                                "sender ID, can be either a valid international " \
                                "format number between 1 and 16 characters " \
                                "long, or an 11 character alphanumeric string."
    def validate_text(self, text):
        return text
    
    def validate_timedelta(self, delta):
        if isinstance(delta, timedelta):
            minutes_from_days = delta.days * 24 * 60
            minutes_from_seconds = delta.seconds / 60
            return minutes_from_days + minutes_from_seconds
        raise ClickatellError, "A timedelta object is required"
    
    def validate_timestamp(self, timestamp):
        if isinstance(timestamp, datetime):
            return timestamp.strftime("%Y-%m-%d %H:%M:%S") # MySQL format
        raise ClickatellError, "A datetime object is required"
    
    def validate_number(self, value):
        if str(value).isdigit():
            return value
        raise ClickatellError, "Must be a numeric value, max: %s" % maximum
    
    def validate(self, *args, **kwargs):
        return self.dispatch(*args, **kwargs)
    

validator = Validator(prefix="validate_")
validate = validator.validate