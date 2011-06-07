"""
Provides the communication mechanism between the Android phones and Nao robot.  
"""


import robot
import toolkit
import atexit
import SocketServer
import threading


"""
Contains the SocketServers for the joystick controller.
"""
server = None



def start():
    """
    Start the joystick server.

    It also registers that they are started.
    """
    global server

    toolkit.verbose("Starting the joystick server...")
    if server:
        toolkit.verbose("Joystick server was already up and running.")
        return
    server = ThreadedTCPServer((toolkit.settings["ANDROID_SERVER_HOST"],
        toolkit.settings["ANDROID_SERVER_PORT"]), AndroidRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()
    toolkit.verbose("Joystick server has started.")



def stop():
    """
    Stop the joystick server.

    It also registers that they are stopped.
    """
    global server

    toolkit.verbose("Stopping the joystick servers...")
    if not server:
        toolkit.verbose("Joystick server is already halted.")
        return
    server.shutdown()
    server = None
    toolkit.verbose("Joystick server has halted.")

atexit.register(stop)


# TODO: Set a right weight for this by empirical testing.
@toolkit.dummy
def transform_phone_movement(kchain_id, movement):
    """
    Transform the phone's movement to something sensible for the robot.

    It currently does nothing; the phone and robot move on a 1:1 scale.
    """
    return movement


class AndroidRequestHandler(SocketServer.StreamRequestHandler):
    """
    The RequestHandler for using an Android phone as joystick.

    The phone sends which arm to control as well as its own movement from its
    accelerator sensors, which corresponds with a movement of the robot's arm.
    When it will hit something, it won't move, and the RequestHandler notifies
    this to its client.  The client should vibrate to notify its user.
    """
    def handle(self):
        """
        Get the request, test whether the movement is legal, and return
        appropriately.
        """
        req = self.rfile.readline().strip()
        kchain_id, phone_movement = \
                req.split(toolkit.settings["MSG_SPLITTER"])
        robot_movement = transform_phone_movement(kchain_id, phone_movement)
        possible = robot.compute_target_position(kchain_id, phone_movement)
        self.wfile.write(possible)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass
