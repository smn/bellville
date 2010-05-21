from clickatell import url as urllib
import logging

class HttpClient(object):
    
    def parse_line(self, line):
        return map(lambda s: s.strip(), line.split(":", 1))
    
    def parse_content(self, content):
        return [self.parse_line(line.strip())
                for line in content.split('\n')
                if line.strip()]
    
    def open(self, method, url, data, headers):
        request, response = urllib.open(method, url, data, headers)
        content = response.read()
        logging.debug('Received: %s' % content)
        return self.parse_content(content)
    
    def get(self, url, data={}, headers={}):
        return self.open('get', url, data, headers)
    
    def post(self, url, data={}, headers={}):
        return self.open('post', url, data, headers)
    