# TODO implement GASymbol.evaluate and interpret the reply of GAViewer
import settings

import collections
import numbers


class GASymbol(object):
    def __init__(self, typ, value):
        self.type = typ
        self.value = value

    def evaluate(self):
        pass

    def is_terminal(self):
        return self.type in [GATypes.variable, GATypes.value]

    def __str__(self):
        return str(self.value)

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
    def __xor__(self, right_value):
        return self._operator('^', self, right_value)
    def __lshift__(self, right_value):
        return self._operator('lcont', self, right_value)
    def __rshift__(self, right_value):
        return self._operator('rcont', self, right_value)

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
    def __rxor__(self, left_value):
        return self._operator('^', left_value, self)
    def __rlshift__(self, left_value):
        return self._operator('lcont', left_value, self)
    def __rrshift__(self, right_value):
        return self._operator('rcont', left_value, self)

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
    def __ixor__(self, right_value):
        return self._operator('^', self, right_value)
    def __ilshift__(self, right_value):
        return self._operator('lcont', self, right_value)
    def __irshift__(self, right_value):
        return self._operator('rcont', self, right_value)


    def __neg__(self):
        return self._operator('-', self)
    def __pos__(self):
        return self._operator('+', self)
    def __abs__(self):
        return self._operator('abs', self)
    def __invert__(self):
        return self._operator('inverse', self)



class GAOperator(GASymbol):
    implemented_operators = {
            '+': [1, 2],    # +
            '-': [1, 2],    # -
            '*': [2],       # *
            '/': [2],       # / through __div__ and __truediv__
            '^': [2],       # ** and ^
            'lcont': [2],   # <<
            'rcont': [2],   # >>
            'abs': [1],     # abs()
            'inverse': [1], # ~
        }


    def __init__(self, operator, *values):
        try:
            arity = GAOperator.implemented_operators[operator]
        except KeyError:
            raise NotImplementedError('Operator %s is not implemented.')
        if len(values) not in arity:
            raise ValueError(
                    'Operator %s has %s arguments, but needs %s arguments.' %
                    (operator, len(values), arity))
        arity = len(values)

        vals = None
        for position, val in enumerate(values):
            if isinstance(val, GASymbol):
                if vals:
                    vals.append(val)
                continue
            if not vals: 
                vals = list(values[0:position])
            try:
                vals.append(symbol(val))
            except ValueError as e:
                raise ValueError('Argument #%s is inappropriate. %s' %
                        (position, e.message))
        if vals:
            values = tuple(vals)

        self.operator = operator
        self.arity = arity
        GASymbol.__init__(self, GATypes.operator, values)


    def __str__(self):
        if self.arity == 0:
            return str(self.operator)
        if self.is_prefix_operator():
            return "%s(%s)" % (str(self.operator), ', '.join(map(str, self.value)))
        arg_strs = []
        for val in self.value:
            if val.is_terminal():
                arg_strs.append(str(val))
            else:
                arg_strs.append('(%s)' % str(val))
        return (' ' + str(self.operator) + ' ').join(arg_strs)


    def is_prefix_operator(self):
        return self.arity < 2 or 'cont' in self.operator
 


class GATypes(object):
    variable = 0
    value = 1
    operator = 2



def symbol(value):
    if isinstance(value, basestring):
        if value[0].isalpha() and value.isalnum():
            return GASymbol(typ=GATypes.variable, value=value)
        if all(map(lambda x: x.isdigit(), value.split('e'))):
            return symbol(value)

    if isinstance(value, settings.NUMBER_TYPE) or \
            isinstance(value, numbers.Number):
        return GASymbol(typ=GATypes.value, value=value)

    raise ValueError("Can't represent this value as a variable or" +
            "numeric value.")


def operator(operator):
    return lambda *values: GAOperator(operator, *values)


add = operator('+')
minus = operator('-')
times = operator('*')
div = operator('/')
lcont = operator('lcont')
rcont = operator('rcont')
inv = operator('inverse')
