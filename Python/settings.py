""" It isn't clear yet whether I will use float, double, decimal.Decimal or
something else for numeric representations.
"""


def verbose(msg, level=1):
    if VERBOSITY >= level:
        print msg

# Temporary, until settings.ini gets interpreted!

# Level of verbosity.  Determines how detailed the messages from the system will be.
VERBOSITY = 1

# This is the server the Android phones should connect to.
ANDROID_SERVER_HOST = localhost
ANDROID_SERVER_PORT = 4000

# All request for kinematics should go to this server.
KINEMATICS_SERVER_HOST = localhost
KINEMATICS_SERVER_PORT = 4001

# The robot is controlled through naoqi.
NAOQI_HOST = localhost
NAOQI_PORT = 9559

# Which type numeric values should be
NUMBER_TYPE = float