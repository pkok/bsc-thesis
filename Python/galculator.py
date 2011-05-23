import settings

import collections
import numbers


class GASymbol(object):
    def __init__(self, typ, value):
        self.type = typ
        self.value = value

    def evaluate(self):
        pass

    @staticmethod
    def _operator(operator, arity, *values):
        return GAOperator(operator, arity, *values)

    def __add__(self, right_value):
        return self._operator('+', self, right_value)
    def __sub__(self, right_value):
        return self._operator('-', self, right_value)
    def __mul__(self, right_value):
        return self._operator('*', self, right_value)
    def __div__(self, right_value):
        return self._operator('/', self, right_value)
    def __truediv__(self, right_value):
        return self._operator('/', self, right_value)
    def __pow__(self, right_value):
        return self._operator('^', self, right_value)

    def __radd__(self, left_value):
        return self._operator('+', left_value, self)
    def __rsub__(self, left_value):
        return self._operator('-', left_value, self)
    def __rmul__(self, left_value):
        return self._operator('*', left_value, self)
    def __rdiv__(self, left_value):
        return self._operator('/', left_value, self)
    def __rtruediv__(self, left_value):
        return self._operator('/', left_value, self)
    def __rpow__(self, left_value):
        return self._operator('^', left_value, self)

    def __iadd__(self, right_value):
        return self._operator('+', self, right_value)
    def __isub__(self, right_value):
        return self._operator('-', self, right_value)
    def __imul__(self, right_value):
        return self._operator('*', self, right_value)
    def __idiv__(self, right_value):
        return self._operator('/', self, right_value)
    def __itruediv__(self, right_value):
        return self._operator('/', self, right_value)
    def __ipow__(self, right_value):
        return self._operator('^', self, right_value)

    def __neg__(self):
        return self._operator('-', self)
    def __pos__(self):
        return self._operator('+', self)
    def __abs__(self):
        return self._operator('abs', self)
    def __inv__(self):
        return self._operator('inverse', self)



class GAOperator(GASymbol):
    def __init__(self, operator, arity, *values):
        if len(values) != arity:
            raise ValueError('Operator %s has %s arguments, but needs %n
            arguments.' % (operator, len(values), arity))

        vals = None
        for position, val in enumerate(values):
            if isinstance(val, numbers.Number) or isinstance(val,
                    settings.NUMBER_TYPE):
                if not vals: 
                    vals = list(values[0:position])
                vals.append(make_value(val))
                continue
            if isinstance(val, GASymbol):
                if vals:
                    vals.append(val)
                continue
            raise ValueException('Argument #%s is inappropriate' %
                    position)
        if vals:
            values = tuple(vals)

        self.operator = operator
        GASymbol.__init__(self, GATypes.operator, values)
 


class GATypes(object):
    variable = 0
    value = 1
    operator = 2



def make_variable(name):
    if name[0].isalpha() and name.isalnum():
        return GASymbol(type=GATypes.variable, value=name)
    raise ValueError('The name of the GA.var symbol is inappropriate.')



def make_value(value):
    if isinstance(value, settings.NUMBER_TYPE) or isinstance(value,
            numbers.Number):
        return GASymbol(type=GATypes.value, value=value)
    raise ValueError('The value of the GA.value is not a Number or %s' %
            settings.NUMBER_TYPE)
