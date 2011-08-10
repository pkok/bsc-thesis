import toolkit

import nao as Robot
import wiimote as Controller

import threading

def main(*args, **kwargs):
    options = getopts(args, kwargs)
    process_options(options)
    robot = Robot.get_instance()
    limb_controllers = []
    for index, limb in enumerate(robot.get_limbs()):
        controller = None
        toolkit.verbose("Put the controller in connectivity mode.")
        while controller is None:
            try:
                controller = Controller.get_instance(index)
                limb_controllers.append(LimbControlThread(robot, limb, controller))
            except RuntimeError, e:
                if "wiimote connection" in e.message:
                    toolkit.verbose("! Connection failed:. Please try again.")
                else:
                    raise
        toolkit.verbose("Paired controller %d with limb '%s'" % (index, limb))
    for control_thread in limb_controllers:
        control_thread.start()
    toolkit.verbose("Press enter to quit the session.")
    while True:
        if not raw_input(''):
            break
    for control_thread in limb_controllers:
        control_thread.terminate()
    robot.terminate()
    toolkit.verbose("Quitting the system. Goodbye!")


@toolkit.dummy
def process_options(options):
    pass


def LimbControlThread(threading.Thread):
    def __init__(self, robot, limb, controller):
        threading.Thread.__init__(self, name=limb)

        self.robot = robot
        self.limb = limb
        self.controller = controller

        self.alive = True


    def terminate(self):
        self.alive = False


    def run(self):
        while self.alive and not self.controller.is_calibrated():
            pass
        while self.alive:
            status = self.controller.get_status()
            if status == Controller.DISCONNECTED:
                self.terminate()
            elif status == Controller.NEW_POSITION:
                position = self.controller.get_position()
                permission = self.robot.position_state(self.limb, position)
                if permission == Robot.POSITION_OKAY:
                    self.robot.move(self.limb, position)
                self.controller.generate_feedback(permission)
        try:
            self.controller.close()
        except:
            pass
