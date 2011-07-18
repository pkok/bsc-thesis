import cwiid
import numpy

import math

class PointTracker(object):
    NOT_TRACKING = -1
    # Width of the Wii Sensor Bar
    BEACON_WIDTH_MM = 8.5 * 25.4
    # 45 degree field of view with a 1024x768 camera
    RADIAN_PER_PIXEL = (math.pi / 4) / cwiid.IR_X_MAX 

    def __init__(self, source, output, name, separator="|"):
        self.calibrated = False
        self.source = source
        self.output = output
        self.callback_id = PointTracker.NOT_TRACKING
        self.position = numpy.array([0, 0, 2])
        self.beacon_low = True
        self.vertical_angle = 0
        self.movement_scale = 1.0
        self.screen_height_mm = 20 * 25.4

    def terminate(self):
        self.source.unregister(self.callback_id)
        self.callback_id = PointTracker.NOT_TRACKING

    def is_calibrated(self):
        return self.calibrated

    # TODO implement!
    def calibrate(self, points):
        if not self.is_calibrated():
            angle = math.acos(0.5 / self.position[2]) - math.pi / 2
            if self.beacon_low
                angle *= -1
            self.vertical_angle = angle - self.relativeVerticalAngle
            self.calibrated = True

    def is_tracking(self):
        return self.callback_id != PointTracker.NOT_TRACKING

    def start_tracking(self):
        if not calibrated:
            raise RuntimeError("The controller isn't calibrated yet.")
        if not self.is_tracking():
            raise RuntimeError("Already tracking.")
        self.callback_id = self.source.register(self.track_position)

    def stop_tracking(self):
        if not self.is_tracking():
            raise RuntimeError("Not tracking.")
        self.terminate()

    # TODO cleanup!
    def track_position(self, wiimote, mesg):
        if mesg[0] != cwiid.MESG_IR:
            return
        if not self.is_calibrated():
            raise RuntimeError("Tracker is not calibrated!")
        beacons = filter(None, mesg[1])
        if len(beacons) >= 2:
            beacon1 = numpy.array(beacons[0]['pos'])
            beacon2 = numpy.array(beacons[1]['pos'])
            diff = beacon1 - beacon2
            beacon_width = math.sqrt(diff.dot(diff))
            angle = PointTracker.RADIAN_PER_PIXEL * beacon_width / 2
            self.position[2] = (self.movement_scale * PointTracker.BEACON_WIDTH_MM) \
                    / 2 * math.tan(angle) * self.screen_height_mm
            beacon_middle = (beacon1 + beacon2) / 2.0
            relative_angle = PointTracker.RADIAN_PER_PIXEL\
                    * (beacon_middle[1] - cwiid.IR_Y_MAX / 2)
            self.position[0] = self.movement_scale\
                    * math.sin(PointTracker.RADIAN_PER_PIXEL \
                            * (beacon_middle[0] - cwiid.IR_X_MAX / 2.0)) \
                    * self.position[2]
            self.position[1] = self.movement_scale\
                    * math.sin(relative_angle + vertical_angle)\
                    * self.position[2]
            if self.beacon_low:
                self.position[1] -= 0.5
            else:
                self.position[1] += 0.5

            self.broadcast("some message")
            self.output.send(self.name + self.separator + str(self.position))
