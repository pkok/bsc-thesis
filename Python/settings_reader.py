import types
"""
Reads .ini-like files.

Unlike ConfigParser and friends, this reader does not handle [sections].
"""

## Settings ##

# Which symbols should be used as a comment?
comment_symbols = "#"

# Variables with these values will be converted to a boolean type.
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


def _interpret(value):
    try_types = [int, float, _boolean, _type]
    for typ in try_types:
        try:
            return typ(value)
        except:
            continue
    return value


def read_settings(filename):
    f = open(filename)
    settings = dict()
    for line in f:
        # Don't process comments
        if not any(line.startswith(symbol) for symbol in comment_symbols): 
            values = map(str.strip, line.split("=", 1))
            if not values[0]: # skip on empty lines
                continue
            if len(values) == 1:
                values.append("None")
            settings[values[0]] = _interpret(values[1])
    return settings
