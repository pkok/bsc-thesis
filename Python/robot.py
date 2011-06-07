"""
Handles reasoning about sensor data and the actual movement.  It communicates
mostly with the IKSolver module (Java).
"""


import toolkit
try:
    import naoqi
except ImportError:
    import dummy_naoqi as naoqi
import operator

robot = None

def start():
    """
    Connect with the NAO robot.

    You can set to which NaoQi server to connect in settings.ini.
    """
    global robot

    # TODO: make a NAO_model
    toolkit.verbose("Connecting with the Nao at %s:%s" %
            (toolkit.settings["NAOQI_HOST"], toolkit.settings["NAOQI_PORT"]))
    robot = NAO(None, toolkit.settings["NAOQI_HOST"], toolkit.settings["NAOQI_PORT"])
    robot.connect()
    toolkit.verbose("Connected!")



def stop():
    """
    Disconnect from the NAO robot.
    """
    global robot

    toolkit.verbose("Closing connection with Nao at %s:%s" %
            (toolkit.settings["NAOQI_HOST"], toolkit.settings["NAOQI_PORT"]))
    if not robot.proxies:
        toolkit.verbose("Already disconnected.")
        return
    robot.close_connections()
    robot = None
    toolkit.verbose("Disconnecting succesful!")



@toolkit.untested
def move(kchain_id, movement):
    """
    Translate the end effector of kinematic chain kchain_id over movement.

    If the robot can move its end effector of kchain_id over movement, it will
    make this move and this function returns toolkit.settings["SIG_MOVE_OKAY"].
    Otherwise, this returns toolkit.settings["SIG_NO_MOVE"].
    """
    try:
        target = compute_target_position(kchain_id, movement)
    except OutOfScannerRangeException as e:
        target = e.args[0]["off plane"]
    if robot.free_space(target):
        robot.move(kchain_id, target)
        return toolkit.settings["SIG_MOVE_OKAY"]
    return toolkit.settings["SIG_NO_MOVE"]



@toolkit.untested
def compute_target_position(kchain_id, motion):
    if robot is None or not robot.is_connected():
        toolkit.verbose("It seems that the system is not setup properly. " \
                + "Did you run all start() sequences?")
        return False

    target = robot.kinematic_chain[kchain_id] + motion
    laser_plane = robot.get_laser_plane()

    if not in_plane(target, laser_plane):
        new_target = orthogonal_projection(target, laser_plane)
        difference = dist(new_target, target)
        if abs(difference) > toolkit.settings['SCANNER_AREA_STICKINESS']:
            details = {"off plane": target,\
                    "on plane": new_target,\
                    "difference": difference}
            raise OutOfScannerRangeException, details
        target = new_target
    return target



@toolkit.dummy
def orthogonal_projection(point, plane):
    return point



@toolkit.dummy
def in_plane(point, plane):
    return True



def dist(x, y):
    """
    Compute the norm of the difference vector of x and y.

    So that is ||x - y||^2 == (x - y) . (x - y)
    """
    diff = map(operator.sub, x, y)
    return sum(map(operator.mul, diff, diff))



class OutOfScannerRangeException(BaseException):
    pass



class NAO(object):
    required_proxies = [
            'ALMotion', 
            'ALLaser', 
            'ALLeds',
            'ALMemory',
            'ALTextToSpeech',
            ]
    kinematic_chains = [
            'Head',
            'LArm', 
            'RArm',
            'LLeg',
            'RLeg',
            'Torso',
            ]

    def __init__(self, model, host, port):
        self.model = model
        self.host = host
        self.port = port
        self.proxies = dict()

    def close_connections(self):
        for proxy_name in self.proxies.keys():
            self.proxies[proxy_name].exit()
            del self.proxies[proxy_name]

    def connect(self):
        """
        Connect to the robot and make all required proxies.
        """
        if self.proxies:
            self.close_connections()
        for req_proxy in self.required_proxies:
            self.proxies[req_proxy] = naoqi.ALProxy(req_proxy, self.host,
                    self.port)

    @toolkit.untested
    def is_connected(self):
        return all(req_proxy in self.proxies\
                for req_proxy in self._required_proxies)

    @toolkit.untested
    def move(self, kchain, target):
        """
        Move an end effector to a target point.
        """
        import motion
        self.proxies["ALMotion"].setPosition(kchain, motion.SPACE_TORSO,
                target, toolkit.settings["NAO_MAXSPEED"], 7)

    @toolkit.dummy
    def get_laser_plane(self):
        raise NotImplementedError, "Will be implemented in a later stadium."

    @toolkit.dummy
    def free_space(self, target):
        """
        Check if target is an unoccupied space.
        """
        raise NotImplementedError, "Will be implemented in a later stadium."
