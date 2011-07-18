#!/usr/bin/env python
from threads import Callback, PatternRumbler

import cwiid
#import numpy

import atexit
#import collections
#import math
#import socket
#import sys

# TODO implement a "controller" model. It should implement at least:
#    .is_calibrated()
#    .calibrate([{"pos": (int, int), "size": int} OR None] * 4)
#    .start_tracking()
#    .stop_tracking()


# I have two Wiimotes, and have marked one of them with a piece of tape. This
# are their MAC addresses, for quick connections.
WIIMOTE_NOTAPE = '00:1E:35:0F:4B:E9'
WIIMOTE_TAPE = "00:25:A0:B3:00:EB"

def require(rpt_mode):
    def _require(callback_fn):
        callback_fn.require = rpt_mode
        return callback_fn
    return _require

@require(cwiid.RPT_BTN)
def callback_disconnect(wiimote, timestamp, mesgs):
    for mesg in mesgs:
        if mesg[0] == cwiid.MESG_BTN\
                and mesg[1] & cwiid.BTN_1 and mesg[1] & cwiid.BTN_2:
            print "disconnecting"
            wiimote.close()
            return

@require(cwiid.RPT_BTN)
def callback_calibrate(controller):
    def _callback_calibrate(wiimote, timestamp, mesgs):
        if not controller.is_calibrated():
            for mesg in mesgs: 
                if mesg[0] == cwiid.MESG_BTN and mesg[1] & cwiid.BTN_HOME:
                    rpt_mode = wiimote.rpt_mode
                    wiimote.rpt_mode ^= cwiid.RPT_IR
                    if controller.calibrate(wiimote.state['ir_src']):
                        return
                    wiimote.rpt_mode = rpt_mode
    return _callback_calibrate

@require(cwiid.RPT_BTN)
def callback_trigger_tracking(controller):
    def _callback_trigger_tracking(wiimote, timestamp, mesgs):
        if controller.is_calibrated():
            for mesg in mesgs:
                if mesg[0] == cwiid.MESG_BTN and mesg[1] & cwiid.BTN_B:
                    controller.start_tracking()
                else:
                    controller.stop_tracking()
            pass
    return _callback_trigger_tracking


class DummyController(object):
    calibration = False
    @staticmethod
    def is_calibrated(*args, **kwargs):
        return Controller.calibration
    @staticmethod
    def calibrate(*args, **kwargs):
        Controller.calibration = True
    def start_tracking(self):
        pass
    def stop_tracking(self):
        pass


class Wiimote(object):
    @property
    def w(self):
        return self.__wiimote

    def __init__(self, bdaddr=None, led=0, rpt_mode=0):
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

        self._pattern_rumble = PatternRumbler(self)
        # FIXME See threads.PatternRumbler
        #self._pattern_rumble.start()
        self._callback = Callback(self)
        self._callback.start()

        atexit.register(self.close)

    def close(self):
        self._callback.terminate()
        self._pattern_rumble.terminate()
        self.__wiimote.close()

    def register(self, fn):
        self._callback.register(fn)

    def unregister(self, fn_id):
        self._callback.unregister(fn_id)

    def notify_callbacks(self):
        self._callback.notify(mesg)

    def rumble_pattern(self, pattern, repeat=False):
        return self._pattern_rumble.set_pattern(pattern, repeat)

    def rumble_stop(self):
        return self._pattern_rumble.stop()

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
