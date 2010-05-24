import re

class Response(object):
    kind = None
    key_value_pattern = re.compile(r'([a-zA-Z]+)\: ([a-zA-Z0-9]+)')
    
    def __init__(self, data):
        self.data = data
        self.process(self.data)
    
    def parse_parts(self, data):
        """
        Parses incoming data like:
        
            312312312312 To: 27123456789
        
        To:
        
            '312312312312', {'To':'27123456789'}
        
        """
        collection = {}
        while 1:
            match = self.key_value_pattern.search(data)
            if match is None:
                break
            key, value = match.group(1, 2)
            collection[key] = value
            data = data.replace(match.group(0), '')
        return data.strip(), collection
    
    def process(self, data):
        """
        Override this method if you're expecting data in a different format.
        """
        self.value, self.extra = self.parse_parts(data)
    
    def __repr__(self):
        return "%s: %s" % (self.kind, self.data)

class OKResponse(Response):
    kind = "OK"
    
class ERRResponse(Response):
    kind = "ERR"
    
    def process(self, string):
        parts = string.split(", ", 1)
        self.code = int(parts[0])
        self.reason = ''.join(parts[1:]).strip() 

class IDResponse(Response):
    kind = "ID"
