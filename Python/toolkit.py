import ConfigParser
import types
#import numpy
#import numpy.linalg


_boolean_states = {'1': True, 'yes': True, 'true': True, 'on': True,
                   '0': False, 'no': False, 'false': False, 'off': False}

def _boolean(value):
    """Try to interpret a string as a boolean value.

    It accepts more values than bool().
    """
    if value.lower() not in _boolean_states:
        raise ValueError, 'Not a boolean: %s' % value
    return _boolean_states[v.lower()]


def _type(kls):
    """Interpret a string to get the corresponding type.

    Example usage:
    >>> _type("float")
    <type 'float'>
    >>> _type("datetime.datetime")
    <type 'datetime.datetime'>
    """
    parts = kls.split('.')
    if len(parts) == 1:
        kls = kls[0].upper() + kls[1:]
        return getattr(types, kls + "Type")
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m


def interpret(value):
    try_types = [int, float, _boolean, _type]
    for typ in try_types:
        try:
            return typ(value)
        except:
            continue
    return value


config_comment_symbol = "#"

def read_config(filename):
    f = open(filename)
    settings = dict()
    for line in f:
        if not line.startswith(config_comment_symbol): # Don't process comments
            values = map(lambda x: x.strip(), line.split("=", 1))
            if not values[0]: # skip on empty lines
                continue
            if len(values) == 1:
                values.append("None")
            settings[values[0]] = interpret(values[1])
    return settings

settings = read_config('../settings.ini')


zero = settings["NUMBER_TYPE"]("0")
one = settings["NUMBER_TYPE"]("1")

def verbose(message, level=1):
    if settings["VERBOSITY"] >= level:
        print message

class interval(object):
    """
    A more abstract notion of and not iterable version of range.

    You can test whether an object is in the interval, and change the interval
    through its properties.
    """
    def __init__(self, start, end, include_start=True, include_end=True):
        self.start = start
        self.end = end
        self.include_start = include_start
        self.include_end = include_end

    def __contains__(self, value):
        pass

    @property
    def interval(self):
        return self.start, self.end

    @interval.setter
    def interval(self, value):
        self.start, self.end = value

    def includes(self, value):
        start_cmp = cmp(value, self.start)
        end_cmp = cmp(self.end, value)
        if start_cmp < 0 or end_cmp > 0:
            return False
        if not self.include_start and start_cmp == 0:
            return False
        if not self.include_end and end_cmp == 0:
            return False
        return True

    @property
    def empty(self):
        return interval(zero, zero)
