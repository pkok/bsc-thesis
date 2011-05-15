"""
Handles reasoning about sensor data and the actual movement.  It communicates
mostly with the IKSolver module (Java).
"""


import settings
import naoqi

robot = None

def start():
    global robot

    # TODO: make a NAO_model
    robot = NAO(None, settings.NAOQI_HOST, settings.NAOQI_PORT)
    robot.connect()



def stop():
    global robot

    robot.close_connections()
    robot = None



class NAO(object):
    required_proxies = [
            'ALMotion', 
            'ALLaser', 
            'ALLeds',
            'ALMemory',
            'ALTextToSpeech',
            ]
    kinematic_chain = {
            'HEAD': 'Head',
            'LEFT_ARM': 'LArm', 
            'RIGHT_ARM': 'RArm',
            'LEFT_LEG': 'LLeg',
            'RIGHT_LEG': 'RLeg',
            'TORSO': 'Torso',
            }

    def __init__(self, model, host, port):
        self.model = model
        self.host = host
        self.port = port
        self.proxies = dict()

    def __del__(self):
        self.close_connections()
        del super(type(self), self)

    def close_connections(self):
        for proxy_name, proxy in self.proxies.itervalues():
            proxy.exit()
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
