from clickatell.errors import ClickatellError

class Dispatcher(object):
    
    def __init__(self, prefix="do_"):
        self.prefix = prefix
    
    def dispatch(self, command, *args, **kwargs):
        command_name = '%s%s' % (self.prefix, command.lower())
        if hasattr(self, command_name):
            fn = getattr(self, command_name)
            return fn(*args, **kwargs)
        raise ClickatellError, 'No dispatcher available for %s' % command
    
