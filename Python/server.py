"""
Provides the communication mechanism between the Android phones and Nao robot.  
"""


import robot
import settings
import SocketServer
import thread


"""
Contains the SocketServers for the left and right joystick controller.
"""
server = {'LEFT': None, 'RIGHT': None}


def start():
    """
    Call this to start the left and right joystick servers.

    It registers that they are started.
    """
    if server['LEFT'] is None:
        _start_left_server()
    if server['RIGHT'] is None:
        _start_right_server()



def stop():
    """
    Call this to stop the left and right joystick servers.

    It registers that they are stopped.
    """
    if server['LEFT']:
        _stop_left_server()
    if server['RIGHT']:
        _stop_right_server()



class BaseAndroidRequestHandler(SocketServer.StreamRequestHandler):
    """
    The base RequestHandler for using an Android phone as joystick.

    The phone sends its movement from its accelerator sensors, which
    corresponds with a movement of the robot's arm.  When it will hit
    something, it won't move, and the RequestHandler notifies this to its
    client.  The client should vibrate to notify its user.

    Subclasses should provide self.which_arm, and set it with a value of
    BaseAndroidRequestHandler.WHICH_ARM.
    """

    WHICH_ARM = {'LEFT': 0, 'RIGHT': 1}

    def handle():
        """
        Get the request, test whether the movement is legal, and return
        appropriately.
        """
        req = self.rfile.readline().strip()
        possible = robot.move_arm(self.which_arm, req)
        self.wfile.write(possible)



class LeftAndroidRequestHandler(BaseAndroidRequestHandler):
    """
    The RequestHandler for an Android phone controlling the left robot hand.
    """
    self.which_arm = BaseAndroidRequestHandler.WHICH_ARM['LEFT']



class RightAndroidRequestHandler(BaseAndroidRequestHandler):
    """
    The RequestHandler for an Android phone controlling the right robot hand.
    """
    self.which_arm = BaseAndroidRequestHandler.WHICH_ARM['RIGHT']



def _start_left_server():
    """
    Start the server for the left joystick.

    It listens in a separate thread.
    """
    server['LEFT'] = SocketServer.TCPServer((settings.ANDROID_SERVER_HOST,
        settings.ANDROID_SERVER_PORT_LEFT), LeftAndroidRequestHandler)
    thread.start_new_thread(server['LEFT'].serve_forever, None)



def _stop_left_server():
    """
    Stop the server for the left joystick.
    """
    server['LEFT'].shutdown()
    server['LEFT'] = None



def _start_right_server():
    """
    Start the server for the right joystick.

    It listens in a separate thread.
    """
    server['RIGHT'] = SocketSever.TCPServer((settings.ANDROID_SERVER_HOST,
        settings.ANDROID_SERVER_PORT_RIGHT), RightAndroidRequestHandler)
    thread.start_new_thread(server['RIGHT'].serve_forever, None)



def _stop_right_server():
    """
    Stop the server for the right joystick.
    """
    server['RIGHT'].shutdown()
    server['RIGHT'] = None
