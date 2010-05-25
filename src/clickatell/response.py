import re

class Response(object):
    key_value_pattern = re.compile(r'([a-zA-Z]+)\: ([a-zA-Z0-9]+)')
    
    def __init__(self, data=''):
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
        return "%s: %s" % (self.__class__.__name__, self.data)

class OKResponse(Response):
    pass

class ERRResponse(Response):
    
    def process(self, string):
        parts = string.split(", ", 1)
        code = parts[0]
        reason = ''.join(parts[1:]).strip() # ugly but always returns an empty
                                            # string even if the list only has 
                                            # one item
        # Hideous but Clickatell is very "liberal" in how they format their
        # error responses
        if code.isdigit():
            self.code = int(code)
            self.reason = reason
        else:
            self.code = 0
            self.value = code

class IDResponse(Response): 
    pass

class CreditResponse(Response):
    kind = "Credit"
    
    def process(self, string):
        self.value = float(string)

class ApiMsgIdResponse(Response):
    pass
