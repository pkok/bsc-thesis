#from decimal import Decimal

import numpy
import numpy.linalg

number = float

zero = number("0")
one = number("1")

e0 = numpy.matrix([one, zero, zero, zero]).T
e1 = numpy.matrix([zero, one, zero, zero]).T
e2 = numpy.matrix([zero, zero, one, zero]).T
e3 = numpy.matrix([zero, zero, zero, one]).T

BASE = [e0, e1, e2, e3]

def point(*data):
    return numpy.matrix(sum(map(lambda x: x[0] * x[1],\
            zip(data, BASE)))).T

original_orientation = numpy.matrix([zero, zero, zero])
origin = point(zero)


def distance(p1, p2):
    """Return the Euclidean distance between two joints p1 and p2.
    """
    return numpy.linalg.norm(p1 - p2)


class Joint(object):
    """The location, orientation and constraints of a robot's joint.
    """
    def __init__(self, location, orientation=None, constraints=None):
        if orientation is None:
            orientation = original_orientation
        if constraints is None:
            constraints = Constraints(False, False)
        elif type(constraints) is not Constraints:
            constraints = Constraints(*constraints)

        self.location = location
        self.orientation = orientation
        self.constraints = constraints


class Constraints(list):
    """Rotational and orientational constraints on joints.
    """
    def __init__(self, orientation=False, rotation=False):
        super(type(self), self).__init__((orientation, rotation))
        self[0], self[1] = self._check(orientation, rotation)

    def _check(self, orientation, rotation):
        new_constraints = []
        for constr in (orientation, rotation):
            # If the constraint is not iterable...
            if not getattr(constr, "__iter__", False):
                constraints_changed = True
                constr = [interval.empty, interval.empty, interval.empty]
            # ... or not all of type interval
            elif any(map(lambda x: type(x) is not interval, constr)):
                constraints_changed = True
                new_constr = []
                for interval_ in constr:
                    if not getattr(interval_, "__iter__", False):
                        interval_ = (0, 0)
                    new_constr.append(interval(*interval_))
                constr = new_constr
            new_constraints.append(constr)
        return new_constraints

    @property
    def orientation(self):
        return self[0]

    @orientation.setter
    def orientation(self, value):
        self[0] = value

    @property
    def rotation(self):
        return self[1]

    @rotation.setter
    def rotation(self, value):
        self[1] = value


class interval(object):
    """A more abstract notion and not iterable version of range.

    You can test whether an object is in the interval, and change the interval
    through its properties.
    """
    def __init__(self, start, end, include_start=True, include_end=True):
        self.start = start
        self.end = end
        self.include_start = include_start
        self.include_end = include_end

    def __contains__(self, value):
        return self.start <= value <= self.end

    @property
    def interval(self):
        return (self.start, self.end)

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
