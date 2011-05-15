import numpy
import numpy.linalg
import settings

zero = settings.NUMBER_TYPE("0")
one = settings.NUMBER_TYPE("1")


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
