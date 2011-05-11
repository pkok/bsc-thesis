"""Implementation of FABRIK, as by Aristidou and Lasenby.
"""

from collections import namedtuple

from galgebra import *


TOLERANCE = 0.001


JointRotor = namedtuple("JointRotor", ["axis", "min", "max"])

class Joint():
    def __init__(self, location, rotors):
        self.location = location
        self.rotors = list()
        for rotor in rotors:
            if not isinstance(rotor, JointRotor):
                rotor = JointRotor(*rotor)
            self.rotors.append(rotor)


"""A kinematic chain is represented as follows:
    [torso, [left_shoulder, left_elbow, left_hand], 
            [right_shoulder, right_elbow, right_hand],
            [neck, head, laser]]
"""


def fabrik(kinematic_chain, target_position, distances=None):
    """Standard implementation of FABRIK, as given by Algorithm 1.
    """
    p = kinematic_chain
    t = target_position
    if distances is None:
        d = map(lambda x: norm(x[0].location - x[1].location), \
                zip(p[1:], p[:-1]))
    else:
        d = distances

    # The distance between root and target
    dist = norm(p[0].location - t)
    # Check whether the target is within reach
    if dist > sum(d):
        # The target is unreachable
        for i in range(len(p) - 1):
            r = norm(t - p[i].location)
            labda = d[i] / r
            p[i + 1].location = (1 - labda) * t + labda * p[i].location
    else:
        # The target is reachable; thus, set as b the initial position of the
        # joint p[0]
        b = p[0].location
        # Check whether the distance between the end effector p[-1] and the
        # target t is greater than a tolerance.
        dif_A = norm(p[-1].location - t)
        while dif_A > TOLERANCE:
            # STAGE 1: FORWARD REACHING
            # Set the end effector p[-1] as target t
            p[-1].location = t
            p = _fabrik_stage1(p, t, d)
            # STAGE 2: BACKWARD REACHING
            # Set the root p[0] its initial position.
            p[0].location = b
            p = _fabrik_stage2(p, t, d)
            dif_A = norm(p[-1].location - t)
    return p


def _fabrik_stage1(p, d, t):
    for i in range(len(p) - 2, -1, -1):
        # Find the distance r between the new joint position p[i+1]
        # and the joint p[i]
        r = norm(p[i + 1].location - p[i].location)
        labda = d[i] / r
        # Find the new joint positions p[i]
        p[i].location = (1 - labda) * p[i + 1].location + \
                labda * p[i].location
    return p


def _fabrik_stage2(p, d, t):
    for i in range(0, len(p) - 1):
        # Find the distance r betrween the new joint position p[i] and
        # the joint p[i + 1]
        r = norm(p[i + 1].location - p[i].location)
        labda = d[i] / r
        # Find the new joint position p[i]
        p[i + 1].location = (1 - labda) * p[i + 1].location + \
                labda * p[i].location
    return p


def _rotational_constraint(joint, next_joint, t):
    # Find the line equation L_1
    L = joint.location ^ next_joint.location ^ einf
    # Find the projection O of the target t on line L_1
    O = (t . L) . (1 / L)
    # Find the distance between the point O and the joint position
    dist = norm(O - t)
    # Map the target (rotate and translate) in such a way that O is now
    # located at the axis origin and oriented according to the x and y-axis =>
    # Now it is a 2D simplified problem
    # Find in which quadrant the target belongs
    # Find the ellipse which is associated with that quadrant using the
    # distances q_j = S tan(theta_j) where j = 1, ..., 4
    # Check whether the target is within the ellipse or not
    if in_ellipse:
        pass
        # Use the true target position t
    else:
        pass
        # go to the next step
    # Find the nearest point on ellipse from the target
    # Map (rotate and translate) that point on ellipse via reverse of line 4
    # and use that point as the new target position
    pass
