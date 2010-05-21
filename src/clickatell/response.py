class Response(object):
    kind = None
    
    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs
        self.process(*args, **kwargs)
    
    def __repr__(self):
        return "%s (%s, %s)" % (self.kind, self.args, self.kwargs)

class OKResponse(Response):
    kind = "OK"
    
    def process(self, string):
        self.results = string.split()

class ERRResponse(Response):
    kind = "ERR"
    
    def process(self, string):
        code, description = string.split(", ")
        self.code = int(self.code)
        self.description = description.strip()

