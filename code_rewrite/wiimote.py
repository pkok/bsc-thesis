#!/usr/bin/env python
from threads import WiimoteCallback as Callback, PatternRumbler
import trackers

import cwiid

import atexit

# TODO implement a "controller" model. It should implement at least:
#    .is_calibrated()
#    .calibrate([{"pos": (int, int), "size": int} OR None] * 4)
#    .start_tracking()
#    .stop_tracking()

OKAY = 0
DISCONNECTED = 1
NEW_POSITION = 2

# I have two Wiimotes, and have marked one of them with a piece of tape. This
# are their MAC addresses, for quick connections.
WIIMOTE_NOTAPE = '00:1E:35:0F:4B:E9'
WIIMOTE_TAPE = "00:25:A0:B3:00:EB"

wiimotes = []

def get_instance(*args, **kwargs):
    wiimote = Wiimote(*args, **kwargs)
    wiimote.register(callback_disconnect)
    wiimote.register(callback_calibrate(tracker))

    return wiimote


def require(rpt_mode):
    def _require(callback_fn):
        callback_fn.require = rpt_mode
        return callback_fn
    return _require


@require(cwiid.RPT_BTN)
def callback_disconnect(wiimote, timestamp, mesgs):
    for mesg in mesgs:
        if mesg[0] == cwiid.MESG_BTN and mesg[1] & (cwiid.BTN_1 ^ cwiid.BTN_2):
            print "disconnecting"
            wiimote.terminate()
            return


@require(cwiid.RPT_BTN)
def callback_calibrate(wiimote, timestamp, mesgs):
    if not wiimote.tracker.is_calibrated():
        for mesg in mesgs: 
            if mesg[0] == cwiid.MESG_BTN and mesg[1] & cwiid.BTN_HOME:
                rpt_mode = wiimote.rpt_mode
                wiimote.rpt_mode ^= cwiid.RPT_IR
                if not wiimote.tracker.calibrate(wiimote.state['ir_src']):
                    wiimote.rpt_mode = rpt_mode

@require(cwiid.RPT_BTN)
def callback_trigger_tracking(wiimote, timestamp, mesgs):
    if wiimote.tracker.is_calibrated():
        for mesg in mesgs:
            if mesg[0] == cwiid.MESG_BTN and mesg[1] & cwiid.BTN_B:
                wiimote._new_position = True
            else:
                wiimote._new_position = False
        pass


class Wiimote(object):
    @property
    def w(self):
        return self.__wiimote

    def __init__(self, bdaddr=None, led=0, rpt_mode=0, tracker_cls=PositionTracker):
        if bdaddr is None:
            self.__wiimote = cwiid.Wiimote()
        else:
            self.__wiimote = cwiid.Wiimote(bdaddr)
        self.mesg = (0, [(None, None)])
        def set_mesg(mesg, timestamp):
            self.mesg = timestamp, mesg
        self.__wiimote.mesg_callback = set_mesg
        self.__wiimote.enable(cwiid.FLAG_MESG_IFC)

        self.led = led
        self.rpt_mode = rpt_mode
        self.tracker = tracker_cls(self)

        self._pattern_rumble = PatternRumbler(self)
        # FIXME See threads.PatternRumbler
        #self._pattern_rumble.start()
        self._callback = Callback(self)
        self._callback.start()

        self._new_position = False

        atexit.register(self.terminate)

    def terminate(self):
        self._callback.terminate()
        self._pattern_rumble.terminate()
        self.__wiimote.close()

    def register(self, fn):
        """
        Register callback function.
        """
        return self._callback.register(fn)

    def unregister(self, fn_id):
        """
        Unregister callback function.
        """
        return self._callback.unregister(fn_id)

    def notify_callbacks(self):
        return self._callback.notify(mesg)

    def rumble_pattern(self, pattern, repeat=False):
        return self._pattern_rumble.set_pattern(pattern, repeat)

    def rumble_stop(self):
        return self._pattern_rumble.stop()

    @toolkit.dummy
    def generate_feedback(self, severity):
        if severity:
            self.rumble = True
        else:
            self.rumble = False

    def is_calibrated(self):
        return self.tracker.is_calibrated()

    @toolkit.untested
    def get_status(self):
        state = None
        try:
            state = self.__wiimote.state
        except ValueError, e:
            if e.message == "Wiimote is closed":
                return DISCONNECTED
            raise
        try:
            if self._new_position:
                return NEW_POSITION
        except KeyError, e:
            if e != 'ir_src':
                raise
        return OKAY

    def get_position(self):
        return self.tracker.get_position()

    def get_movement(self):
        return self.tracker.get_movement()

    @property
    def rumble(self):
        return self._rumble
    
    @rumble.setter
    def rumble(self, value):
        self._rumble = value
        self.__wiimote.rumble = self._rumble

    @property
    def state(self):
        return self.__wiimote.state

    @property
    def led(self):
        return self._led

    @led.setter
    def led(self, value):
        self._led = value
        self.__wiimote.led = self._led

    @property
    def rpt_mode(self):
        return self._rpt_mode

    @rpt_mode.setter
    def rpt_mode(self, value):
        self._rpt_mode = value
        self.__wiimote.rpt_mode = self._rpt_mode


if __name__ == "__main__":
    wiimote = Wiimote(WIIMOTE_NOTAPE)
    wiimote.led = 5
