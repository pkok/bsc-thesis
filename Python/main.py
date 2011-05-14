import robot
import server
import settings


if __name__ == "__main__":
    try:
        settings.verbose("Starting the system.")
        robot.start()
        server.start()
    except:
        settings.verbose("Halting the system.")
        robot.stop()
        server.stop()
