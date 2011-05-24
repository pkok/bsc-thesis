"""
Handles reasoning about sensor data and the actual movement.  It communicates
mostly with the IKSolver module (Java).
"""


import toolkit
import naoqi

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



#DUMMY
def move(kinematic_chain, movement):
    """
    Translate the end effector of kinematic_chain over movement.

    Dummy method; it needs more implementating!
    """
    if robot is None or not robot.is_connected():
        return False
    return kinematic_chain in NAO.kinematic_chains



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

    def is_connected(self):
        for req_proxy in self.required_proxies:
            if not self.proxies.has_key[req_proxy]:
                return False
        return True
