from robot_parts import *

class NAO(object):
    HEAD = "head"
    RIGHT = "right arm"
    LEFT = "left arm"

    NECK_OFFSET_Z = 126.50
    LASER_OFFSET_Z = 106.60
    SHOULDER_OFFSET_Y = 98.00
    SHOULDER_OFFSET_Z = 100.00
    UPPER_ARM_LENGTH = 90.00
    LOWER_ARM_LENGTH = 50.55
    HAND_OFFSET_X = 58.00
    HAND_OFFSET_Z = -15.90

    def __init__(self):
        """Generate the skeletal structure of the robot. 

        It puts all the joints and kinematic chains in the object's "name
        space".
        """
        self.center = Joint(origin, original_orientation, (False, False))
        self.neck = Joint(self.center.location + self.NECK_OFFSET_Z * e3,\
                original_orientation,\
                (False, [False, (number("-38.5"), number("29.5")),\
                    (number("-119.5"), number("119.5"))]))
        self.laser = Joint(self.neck.location + self.LASER_OFFSET_Z * e3,\
                original_orientation,\
                (False, False))

        self.right_shoulder = Joint(self.center.location +\
                self.SHOULDER_OFFSET_Y * e2 + self.SHOULDER_OFFSET_Z * e3,\
                original_orientation,\
                (False, [(number("-94.5"), number("-0.5")),\
                    (number("-119.5"), number("119.5")), False]))
        self.right_elbow = Joint(self.right_shoulder.location +\
                self.UPPER_ARM_LENGTH * e1,\
                original_orientation,\
                (False, [(number("0.5"), number("89.5")), False,\
                    (number("-119.5"), number("119.5"))]))
        self.right_wrist = Joint(self.right_elbow.location +\
                self.LOWER_ARM_LENGTH * e1,\
                original_orientation,\
                (False, [False, False, (number("-104.5"), number("104.5"))]))
        self.right_hand = Joint(self.right_wrist.location + \
                self.HAND_OFFSET_X * e1 + self.HAND_OFFSET_Z * e3,\
                original_orientation,\
                (False, False))

        self.left_shoulder = Joint(-e2.T * self.right_shoulder.location,\
                original_orientation,\
                (False, [(number("0.5"), number("98.5")),\
                    (number("-119.5"), number("119.5")), False]))
        self.left_elbow = Joint(-e2.T * self.right_elbow.location,\
                original_orientation,\
                (False, [(number("89.5"), number("0.5")), False,\
                    (number("-119.5"), number("119.5"))]))
        self.left_wrist = Joint(-e2.T * self.right_wrist.location,\
                original_orientation,\
                (False, [False, False, (number("-104.5"), number("104.5"))]))
        self.left_hand = Joint(-e2.T * self.right_hand.location,\
                original_orientation,\
                (False, False))


        self.kinematic_chain = {
                self.HEAD: [self.center, self.neck, self.laser],
                self.RIGHT: [self.center, self.right_shoulder,\
                    self.right_elbow, self.right_wrist, self.right_hand],
                self.LEFT: [self.center, self.left_shoulder,\
                    self.left_elbow, self.left_wrist, self.left_hand],
        }

        self.distances = {}
        for chain in self.kinematic_chain:
            dist = []
            for joint1, joint2 in zip(self.kinematic_chain[chain],\
                    self.kinematic_chain[chain][1:]):
                d = distance(joint1.location, joint2.location)
                dist.append(d)
            self.distances[chain] = dist

    def compute_move(self, chain_name, target):
        """Compute the angles between the joints for the target position.

        It does not send these changes to the robot.
        """
        if self.kinematic_chain.has_key(chain_name):
            new_chain = fabrik(chain_name, target, self.distances[chain_name])
            self.kinematic_chain[chain_name] = new_chain
            return chain_name, new_chain
        else:
            err_str = "\"%s\" is not a kinematic chain name"
            raise NotImplementedError(err_str % chain_name)
