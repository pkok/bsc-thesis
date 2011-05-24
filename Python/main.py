import robot
import server
import settings
import atexit

def start():
    try:
        settings.verbose("Starting the system.")
        robot.start()
        server.start()
        settings.verbose("Succesfully started the system!")
    except:
        settings.verbose("Uh-oh. An error occured at startup.")


def stop():
    try:
        settings.verbose("Halting the system.")
        robot.stop()
        server.stop()
    except:
        settings.verbose("Uh-oh. An error occured when halting.")

atexit.register(stop)

if __name__ == "__main__":
    start()
