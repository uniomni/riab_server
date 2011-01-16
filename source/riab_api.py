class RiabAPI():
    API_VERSION="0.1a"
    
    def version(self):
        return self.API_VERSION
    
    def test(self):
        print "hello"
        return True