import robot
import server
import toolkit
import atexit

def start():
    try:
        toolkit.verbose("Starting the system.")
        robot.start()
        server.start()
        toolkit.verbose("Succesfully started the system!")
    except:
        toolkit.verbose("Uh-oh. An error occured at startup.")


def stop():
    try:
        toolkit.verbose("Halting the system.")
        robot.stop()
        server.stop()
    except:
        toolkit.verbose("Uh-oh. An error occured when halting.")

atexit.register(stop)

if __name__ == "__main__":
    start()
