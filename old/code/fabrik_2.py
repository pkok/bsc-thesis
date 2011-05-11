from numpy import matrix
from numpy.linalg import norm

from robot_parts import zero, one, BASE, number, distance

TOLERANCE = number("0.001")


def fabrik(p, t, d):
    """Forward And Backward Reaching Inverse Kinematics solver.

    For a discussion of this algorithm, look for an article or technical
    report by Aristidou and Lasenby. I used "CUED/F-INFENG/TR-632".
    """
    # Check whether the target is within reach
    dist = distance(p[0] - t)
    if dist > sum(d):
        p = _fabrik_reach(p, d, unreachable=True, target=t)
    else:
        b = p[0]
        # If the end effector is close enough to the target, finish.
        while distance(p[-1], t) > TOLERANCE:
            # FORWARD REACHING
            p = _fabrik_reach(reversed(p), reversed(d), t)
            # STAGE 2: BACKWARD REACHIN
            p = _fabrik_reach(p, d, b)
    return p


def _fabrik_reach(p, d, start=None, unreachable=False, target=None):
    """Direction independent implementation of the "Reach" steps in FABRIK.

    - p: a list of joints;
    - d: for each d[i] it is the distance between p[i] and p[i + 1];
    - start: the start location of p[0];
    - unreachable: whether the target is reachable;
    - target: the target to reach if unreachable.

    It returns a list of new joint locations and orientations.
    """
    if start is None:
        start = p[0]
    new_p = [start]
    if unreachable:
        p = len(p) * [target]
    for next_p, curr_d in zip(p[1,:], d):
        curr_p = new_p[-1]
        r = distance(next_p, curr_p)
        labda = curr_d / r
        # Find the new joint locationitions
        if len(new_p) > 1:
            prev_p = new_p[-2]
        else:
            prev_p = new_p[-1]
        new_p.append(_update(labda, prev_p, curr_p, next_p))
    return new_p


def _update(labda, prev_p, curr_p, next_p, **kwargs):
    """Update rule for joints.
    """
    return _update_basic(labda=labda, \
            prev_p=prev_p, curr_p=curr_p, next_p=next_p, **kwargs)


def _update_basic(labda, curr_p, next_p, **kwargs):
    """The unconstrained update rule for joints.
    """
    # That "1" should actually be _type("1"), but I guess that'll be a bottle
    # neck, as this will be called quiet often. Coercion should handle this.
    return (1 - labda) * curr_p.location + labda * next_p.location


def _update_ori(labda, curr_p, next_p, **kwargs):
    """The orientational constrained update rule for joints.

    The unconstrained update rule should be implemented.
    """
    new_p = _update_basic(labda=labda, curr_p=curr_p, next_p=next_p, **kwargs)
    orientation = get_orientation(curr_p, next_p)

    new_ori = []

    for axis_orientation, (min_ori, max_ori) in \
            zip(orientation, new_p.constraints.orientation):
        if axis_orientation < min_ori:
            axis_orientation = min_ori
        elif axis_orientation > max_ori:
            axis_orientation = max_ori
        new_ori.append(axis_orientation)

    new_p.orientation = matrix(new_ori)

    return new_p


def _update_rot(labda, prev_p, curr_p, next_p, **kwargs):
    new_p = _update_ori(labda=labda, \
            prev_p=prev_p, curr_p=curr_p, next_p=next_p, **kwargs)
    angles = get_orientation(prev_p, next_p)
    new_angles = []
    angles_changed = False
    for angle, (min_angle, max_angle) in \
            zip(angles, new_p.constraints.rotation):
        if angle < min_angle:
            angle = min_angle
            angles_changed = True
        elif angle > max_angle:
            angle = max_angle
            angles_changed = True
        new_angles.append(angle)
    if angles_changed:
        R = make_rotation_matrix(*angles)
        new_p = (R * (next_p - curr_p)) + curr_p
    return new_p


###def _update_rot(labda, prev_p, curr_p, next_p, **kwargs):
###    """The rotational constrained update rule for joints.
###
###    Orientational constraints are needed for this to be implemented.
###    """
###    new_p = _update_ori(labda=labda, \
###            prev_p=prev_p, curr_p=curr_p, next_p=next_p, **kwargs)
###
###    if prev_p is not curr_p and curr_p is not next_p:
###        projected = (prev_p * new_p.T) * prev_p + (curr_p * new_p.T) * curr_p
###        dist = distance(projected, new_p)
###        angles = get_orientation(curr_p, prev_p)
###        R = make_rotation_matrix(*angles)
###        R.I * matrix([1, 0, 0]) # ???
###        new_angles = []
###        for angle, (min_angle, max_angle) in \
###                zip(angles, new_p.constraints.rotation):
###            if angle < min_angle:
###                angle = min_angle
###            elif angle > max_angle:
###                angle = max_angle
###            new_angles.append(angle)
###        new_p
###
###
###    return new_p


def get_orientation(p1, p2):
    """Return the orientation (x,y,z) of p1 as seen from p2.
    """
    # Translate to the origin
    p1_ = p1 - p1
    p2_ = p2 - p1
    # Get the angles
    angles = []
    for base_nr in len(BASE):
        projected = matrix(p2_, copy=True)
        projected[base_nr] = 0
        angle = (p2_ * projected.T) / (norm(p2_) * norm(projected))
        angles.append(angle)

    if len(BASE) > 3:
        angles = angles[1:]

    return angles


def make_rotation_matrix(angle_x, angle_y, angle_z):
    raise NotImplementedError("make_rotation_matrix is not implemented yet")
