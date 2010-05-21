import re

class Response(object):
    kind = None
    
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs
        self.process(*args, **kwargs)
    
    def __repr__(self):
        return "%s (%s, %s)" % (self.kind, self.args, self.kwargs)

class OKResponse(Response):
    kind = "OK"
    
    def process(self, *args, **kwargs):
        print args, kwargs
        string = args[0]
        self.results = string.split()

class ERRResponse(Response):
    kind = "ERR"
    
    def process(self, string):
        parts = string.split(", ", 1)
        self.code = int(parts[0])
        self.reason = ''.join(parts[1:]).strip() # ugly

class IDResponse(Response):
    kind = "ID"
    re_to = re.compile(r'To: (?P<recipient>\d+)')
    
    def process(self, string):
        parts = string.split(" ", 1)
        apimsg = parts[0]
        remainder = ''.join(parts[1:]).strip() # ugly
        self.apimsgid = parts[0]
        match = self.re_to.match(remainder)
        if match:
            self.to = match.groupdict()['recipient']
            print "TO:",self.to
        else:
            self.to = ''
