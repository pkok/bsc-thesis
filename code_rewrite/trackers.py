import toolkit 

import cwiid
import numpy

import math

class PositionTracker(object):
    NOT_TRACKING = -1
    # Width of the Wii Sensor Bar
    BEACON_WIDTH_MM = 8.5 * 25.4
    # 45 degree field of view with a 1024x768 camera
    RADIAN_PER_PIXEL = (math.pi / 4) / cwiid.IR_X_MAX 

    def __init__(self, wiimote):
        self.calibrated = False
        self.wiimote = wiimote
        self.position = numpy.array([0, 0, 2])
        self.beacon_low = True
        self.vertical_angle = 0
        self.movement_scale = 1.0
        self.screen_height_mm = 20 * 25.4
        self.relativeVerticalAngle = 0

        self._prev_ir_src = None
        self._is_tracking = False
        self._rpt_mode = 0


    def is_calibrated(self):
        return self.calibrated


    def calibrate(self, points):
        if not self.is_calibrated():
            angle = math.acos(0.5 / self.position[2]) - math.pi / 2
            if self.beacon_low
                angle *= -1
            self.vertical_angle = angle - self.relativeVerticalAngle
            self.calibrated = True


    def start_tracking(self):
        self._rpt_mode = self.wiimote.rpt_mode
        self.wiimote.rpt_mode ^= cwiid.RPT_IR
        self._is_tracking = True


    def stop_tracking(self):
        self._is_tracking = False
        self.wiimote.rpt_mode = self._rpt_mode

    
    def is_tracking(self):
        return self._is_tracking


    # TODO cleanup!
    @toolkit.untested
    def get_position(self):
        if not self._is_tracking:
            return

        try:
            ir_src = self.wiimote.state['ir_src']
        except KeyError, e:
            if e.message == 'ir_src':
                raise RuntimeError("The Wiimote has RPT_IR turned off.")

        if ir_src == self._prev_ir_src:
            return self.position

        if not self.is_calibrated():
            raise RuntimeError("Tracker is not calibrated!")

        beacons = filter(None, mesg[1])

        if len(beacons) < 2:
            raise RuntimeError("Not enough beacons visible (%d instead of %d)"
                    % (len(beacons), 2))

        beacon1 = numpy.array(beacons[0]['pos'])
        beacon2 = numpy.array(beacons[1]['pos'])
        diff = beacon1 - beacon2
        beacon_width = math.sqrt(diff.dot(diff))
        angle = PositionTracker.RADIAN_PER_PIXEL * beacon_width / 2
        self.position[2] = (self.movement_scale * PositionTracker.BEACON_WIDTH_MM) \
                / 2 * math.tan(angle) * self.screen_height_mm
        beacon_middle = (beacon1 + beacon2) / 2.0
        relative_angle = PositionTracker.RADIAN_PER_PIXEL\
                * (beacon_middle[1] - cwiid.IR_Y_MAX / 2)
        self.position[0] = self.movement_scale\
                * math.sin(PositionTracker.RADIAN_PER_PIXEL \
                        * (beacon_middle[0] - cwiid.IR_X_MAX / 2.0)) \
                * self.position[2]
        self.position[1] = self.movement_scale\
                * math.sin(relative_angle + vertical_angle)\
                * self.position[2]
        if self.beacon_low:
            self.position[1] -= 0.5
        else:
            self.position[1] += 0.5

        return self.position

    @toolkit.untested
    def get_movement(self):
        original_position = self.position
        return self.get_position - original_position
