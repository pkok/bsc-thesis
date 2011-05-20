"""
Dummy file, for when there is no naoqi installation.
"""

_counter = 0

def ALProxy(one, two, three):
    global _counter
    _counter += 1
    return Proxy(_counter)

class Proxy(object):
    def __init__(self, one):
        self.id = one

    def __repr__(self):
        return "%s(id=%s)" % (self.__class__, self.id)

    def exit(self):
        return self.id
