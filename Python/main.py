import robot
import server


if __name__ == "__main__":
    try:
        robot.start()
        server.start()
    except:
        robot.stop()
        server.stop()
