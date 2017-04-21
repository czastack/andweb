
class FakeQuerySet(object):
    __slots__ = ('data',)
    
    _prefetch_related_lookups = False
    
    def __init__(self, data):
        self.data = data

    def all(self):
        return self
    
    def __getattr__(self, key):
        return getattr(self.data, key)

    def iterator(self):
        return iter(self.data)