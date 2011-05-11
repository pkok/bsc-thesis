import os
import signal
import socket

from robot_parts import *

class GAViewer(object):
    GAVIEWER_PATH = "gaviewer"
    GAVIEWER_NAME = "gaviewer"
    GAVIEWER_STANDARD_PORT = 6860
    LOAD_FILE = ""
    COLORS = ["red", "green", "blue", "white", "magenta", "yellow",\
            "cyan", "black", "gray"]
    MATH_MODELS = {3: "e3ga", 4: "p3ga", 5: "c5ga"}


    def __init__(self, model, ip="localhost", port=6860):
        self.model = model
        self.ip = ip
        # GAViewer doesn't do anything with a specific port. It always
        # uses port 6860.
        self.port = self.GAVIEWER_STANDARD_PORT
        self.__socket = None


    def __del__(self):
        """Close all connections and windows when destroyed.
        """
        self._close_connections()

    def _close_connections(self):
        """Close all connections and windows.
        """
        self.__socket.close()
        self.__socket = None
        os.kill(self.__process_id, signal.SIGKILL)

    def connect(self):
        """Connect to the GAViewer client.
        """
        if self.__socket is not None:
            self._close_connections()
        # Start GAViewer with port, and load the body.
        self.__process_id = os.spawnlp(os.P_NOWAIT, self.GAVIEWER_PATH,\
                self.GAVIEWER_NAME, "-net", str(self.port))
        self.__socket = socket.create_connection((self.ip, self.port))
        self.__socket.send("default_model(%s)$" % self.MATH_MODELS[len(BASE)])
        self.__socket.send(self.body_setup())


    def body_setup(self):
        cmd = ""
        self._chain_name = {}
        for i, chain_name in enumerate(self.model.kinematic_chain):
            self._chain[chain_name] = {
                    "len": len(self.model.kinematic_chain[chain_name]),
                    "number": i,
            }
            for j, joint in enumerate(self.model.kinematic_chain[chain_name]):
                var_name = "%s[%s][%s]" % (self.VAR_BASE, i, j)
                value = self.read_matrix(joint.location)
                cmd += "%s = %s, " % (var_name, value)
        self.__socket.send(cmd + "$")


    def read_matrix(self, matrix):
        axis_labels = ["e1", "e2", "e3"]
        if len(BASE) >= 4:
            axis_labels = ["e0"].extend(axis_labels)
        if len(BASE) >= 5:
            axis_labels.append("einf")
        components = []
        for label, value in zip(axis_labels, matrix):
            components.append("%s * %s" % (label, int(value)))
        return " + ".join(components)


    def send_changes(self, chain_name, new_chain):
        """Send the changed joint positions to GAViewer.
        """
        if not self.__socket:
            self.connect()



class NAO(object):
    def __init__(self, model, ip="localhost", port=9559):
        self.model = model
        self.ip = ip
        self.port = port
        self.__proxy = None


    def __del__(self):
        self._close_connections()


    def _close_connections(self):
        self.__proxy.exit()
        self.__proxy = None


    def connect(self):
        """Connect to the robot and make a new ALMotion object.
        """
        if self.__proxy is not None:
            self._close_connections()
        self.__proxy = naoqi.ALProxy("ALMotion", self.ip, self.port)


    def send_changes(self, new_chain):
        """Send the changed joint positions to the robot.

        It also converts all positions to the angles between joints.
        """
        if not self.__proxy:
            self.connect()
        # Convert positions of joints to angles
