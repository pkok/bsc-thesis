import wiimote
import numpy
import math

MIN_BEACONS = 2
BEACON_WIDTH = 1 # In milimeters
RADIANS_PER_X = (pi * 360 / 33) / wiimote.Wiimote.IR_X_MAX
RADIANS_PER_Y = (pi * 360 / 23) / wiimote.Wiimote.IR_Y_MAX

def get_position(wiimote):
    ir_sources = filter(None, wiimote.state['ir_src'])
    brightest_spots = sorted(ir_sources, key=lambda x: x['size'], 
            reverse=True)
    beacons = map(lambda x: numpy.array(x['pos'] + tuple(x['size'])), 
            brightest_spots)

    if len(beacons) < MIN_BEACONS:
        raise RuntimeError("Not enough beacons visible (%d instead of %d)"
                % (len(beacons), MIN_BEACONS))

    diff = beacons[0] - beacons[1]
    beacon_width = math.sqrt(diff.dot(diff))

    return (horizontal_position, vertical_position, distance)
