import sys
import math

import numpy
import sympy
from sympy.galgebra import GA

GA.set_main(sys.modules[__name__])

basis = "e0 e1 e2 e3 einf"
#metric = "0 0 0 0 -1, 0 # # # 0, 0 # # # 0, 0 # # # 0, -1 0 0 0 0"
metric = "0 0 0 0 -1, 0 1 0 0 0, 0 0 1 0 0, 0 0 0 1 0, -1 0 0 0 0"
GA.MV.setup(basis, metric)


def conformal(point):
    if isinstance(point, GA.MV):
        if point.mv[0] != 0 or point.mv[1] != 0:
            return point
    else:
        point = point[0] * e1 + point[1] * e2 + point[2] * e3
    return e0 + point + (GA.HALF * numpy.dot(point, point) * einf)


def euclidean(point):
    return point.mv[1][1:-1]


def norm(vector):
    prod = vector | vector
    if prod < 0:
        prod *= -1
    return math.sqrt(prod)
