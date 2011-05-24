"""
Provides the communication mechanism between the Android phones and Nao robot.  
"""


import robot
import settings
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

    settings.verbose("Starting the joystick server...")
    if server:
        settings.verbose("Joystick server was already up and running.")
        return
    server = ThreadedTCPServer((settings.ANDROID_SERVER_HOST,
        settings.ANDROID_SERVER_PORT), AndroidRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()
    settings.verbose("Joystick server has started.")



def stop():
    """
    Stop the joystick server.

    It also registers that they are stopped.
    """
    global server

    settings.verbose("Stopping the joystick servers...")
    if not server:
        settings.verbose("Joystick server is already halted.")
        return
    server.shutdown()
    server = None
    settings.verbose("Joystick server has halted.")

atexit.register(stop)


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
        kinematic_chain_id, phone_movement = req.split(settings.MSG_SPLITTER)
        possible = robot.move(kinematic_chain_id, phone_movement)
        self.wfile.write(possible)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass
