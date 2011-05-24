import ConfigParser
import types
import numpy
import numpy.linalg


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
        kls[0] = kls[0].upper()
        return getattr(types, kls + "Type")
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m

class DefaultSectionConfigParser(ConfigParser.RawConfigParser):
    def __init__(self, default_section, *args, **kwargs):
        ConfigParser.RawConfigParser.__init__(self, *args, **kwargs)
        self.default_section = default_section

    def __getitem__(self, option):
        try_types = [int, float, _boolean, _type]
        value = self.get(self.default_section, option)
        for typ in try_types:
            try:
                return typ(value)
            except:
                continue
        return value
        
settings = DefaultSectionConfigParser("default")
settings.readfp(open("../settings.ini"))


zero = settings["NUMBER_TYPE"]("0")
one = settings["NUMBER_TYPE"]("1")

def verbose(message, level=1):
    if settings["VERBOSITY"] >= level:
        print message)

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
