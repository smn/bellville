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
        return ','.join(recipients)
    
    def validate_from(self, _from):
        if _from.isdigit() and len(_from) <= 16:
            return _from
        elif _from.isalnum() and len(_from) <= 11:
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
    
    def validate(self, options):
        # timedeltas, validated to return minutes
        timedeltas = ['deliv_time', 'validity']
        for option in timedeltas:
            if option in options:
                options[option] = self.dispatch('timedelta', options.pop(option))
        
        # number, validated to ensure they are indeed numbers
        numbers = ['concat', 'max_credits', 'req_feat']
        for option in numbers:
            if option in options:
                options[option] = self.dispatch('number', options.pop(option))
        
        # timestamps, returned in Mysql timestamp format
        timestamps = ['scheduled_time']
        for option in timestamps:
            if option in options:
                options[option] = self.dispatch('timestamp', options.pop(option))
        
        # if from is specified then make sure something's been set as the
        # req_feat parameter as well.
        if 'sender' in options:
            options['from'] = self.dispatch('from', options.pop('sender'))
            if 'req_feat' not in options:
                raise ClickatellError, 'When specifying `sender` you also '\
                                        'need to specify the `req_feat` ' \
                                        'parameter'
        return options
        

validator = Validator(prefix="validate_")
validate = validator.validate
