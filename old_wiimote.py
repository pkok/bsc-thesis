#!/usr/bin/env python
import cwiid
import numpy

import atexit
import collections
import math
import socket
import sys

WIIMOTE_TAPE = "00:25:A0:B3:00:EB"
WIIMOTE_NOTAPE = "00:1E:35:0F:4B:E9"
COLOR = ["cyan", "magenta", "yellow", "red", "green", "blue", "black", "white"]
points = collections.defaultdict(lambda: (None, None))
sock = None
wiimotes = []
calibrated = []

def start():
    global sock
    global wiimotes
    sock = connect_ga()
    wiimotes = connect_wiimotes(sock)


def stop():
    global sock
    global wiimotes
    for wiimote in wiimotes:
        wiimote.close()
    wiimotes = []
    if sock:
        sock.close()
        sock = None

atexit.register(stop)

def main():
    start()
    exit = False
    print "Typ \"q\" to quit."
    while not exit:
        c = sys.stdin.read(1)
        if c == 'q' or c == 'Q':
            exit = True
    stop()

def connect_ga(host="localhost", port=6860, init=""):
    """Connect to GAViewer.  Use init to send initialization commands to
    GAViewer, like dynamic{} statements."""
    try:
        s = socket.create_connection((host, 6860))
        # Empty GAViewer from data of a possible previous session.
        s.send("cld(); clf(); clr();$")
        if init:
            s.send(init + "$")
        return s
    except:
        raw_input("Start GAViewer on %s and type \"add_net_port(%s)\"."\
                % (host, port)\
                + "Then, press enter in this window.")
        return connect_ga()


def connect_wiimotes(sock, wiimote_count=-1):
    global points
    global calibrated

    wiimotes = list()
    if wiimote_count < 0:
        wiimote_count = int(raw_input("How many Wii Remotes to connect? "))
    calibrated = wiimote_count * [bool()]
    for wiimote_id in range(wiimote_count):
        raw_input("Put Wii Remote #%d in discovery mode, and press enter. " % (wiimote_id + 1))
        wiimote = cwiid.Wiimote()
        wiimote.led = wiimote_id + 1
        wiimote.rpt_mode = cwiid.RPT_BTN
        wiimote.enable(cwiid.FLAG_MESG_IFC)
        wiimote.mesg_callback = callback(wiimote_id, sock)
        wiimotes.append(wiimote)
        points[wiimote] = numpy.array((0, 0))
        print "Connected to Wii Remote #%d" % (wiimote_id + 1)
    print "All %d Wii Remotes are connected." % wiimote_count
    return wiimotes


def callback(wiimote_id, sock):
    global COLOR
    global wiimotes

    GAVIEWER_MESG = "p%(id)d = %(color)s(%%(mesg)s)%%(displaymode)s$" \
        % { "id": wiimote_id, "color": COLOR[wiimote_id % len(COLOR)]}

    def _send_socket(mesg, is_displayed=True):
        formatting = {"mesg": mesg, "displaymode": ","}
        if not is_displayed:
            formatting["displaymode"] = ";"
        return sock.send(GAVIEWER_MESG % formatting)

    kwargs = {"wiimote_id": wiimote_id, 
            "send_socket": _send_socket}

    def _callback(mesgs, timestamp):
        for mesg in filter(None, mesgs):
            if mesg[0] == cwiid.MESG_BTN:
                if cwiid.BTN_B & mesg[1]:
                    wiimotes[wiimote_id].rpt_mode = cwiid.RPT_BTN ^ cwiid.RPT_IR
                else:
                    wiimotes[wiimote_id].rpt_mode = cwiid.RPT_BTN
                callback_BTN(mesg, timestamp, **kwargs)
            elif mesg[0] == cwiid.MESG_IR:
                callback_IR(mesg, timestamp, **kwargs)
    return _callback

headX = 0
headY = 0
headDist = 2
angle = 0
cameraIsAboveScreen = False
relativeVerticalAngle = 0
cameraVerticalAngle = 0
dotDistanceInMM = 8.5 * 25.4 # width of the wii sensor bar
screenHeightInMM = 20 * 25.4
radiansPerPixel = (math.pi / 4) / 1024 # 45 degree vield of view with a 124x768 camera
movementScaling = 1.


def callback_IR_default(mesg, timestamp, send_socket, wiimote_id=-1, **kwargs):
    global points

    blobs = filter(None, mesg[1])
    if len(blobs) >= 2:
        points[wiimote_id] = (numpy.array(blob[0]['pos']),
                numpy.array(blob[1]['pos']))
        point_pos = "c3ga_point(0.01 %(x).3f e1 - 0.01 %(y).3f e2)"
        send_socket(" ^ ".join([point_pos % {"x": p[0], "y": p[1]}\
                for p in points[wiimote_id]]))


def callback_BTN_default(mesg, timestamp, **kwargs):
    pass

def callback_track_BTN(mesg, timestamp, send_socket=None, wiimote_id=-1, **kwargs):
    global calibrated
    global angle
    global cameraIsAboveScreen
    global cameraVerticalAngle, relativeVerticalAngle

    if not calibrated[wiimote_id] and cwiid.BTN_A & mesg[1]:
        # angle of head to screen
        angle = math.acos(.5 / headDist) - math.pi / 2
        if not cameraIsAboveScreen:
            angle *= -1
        cameraVerticalAngle = angle - relativeVerticalAngle
        calibrated[wiimote_id] = True
        print "Calibrated"

def callback_track_IR(mesg, timestamp, send_socket=None, wiimote_id=-1, **kwargs):
    global calibrated
    global points
    global headX, headY, headDist, angle
    global cameraIsAboveScreen
    global cameraVerticalAngle, relativeVerticalAngle
    global dotDistanceInMM, screenHeightInMM, radiansPerPixel, movementScaling

    if not calibrated[wiimote_id]:
        print "Not calibrated!"
        return
    blobs = filter(None, mesg[1])
    if len(blobs) >= 2:
        p1 = numpy.array(blobs[0]['pos'])
        p2 = numpy.array(blobs[1]['pos'])
        points[wiimote_id] = (p1, p2)
        diff = p1 - p2
        p_dist = math.sqrt(diff.dot(diff))
        angle = radiansPerPixel * p_dist / 2
        headDist = movementScaling * dotDistanceInMM
        headDist /= 2 * math.tan(angle) * screenHeightInMM

        avg = (p1 + p2) / 2.

        headX = movementScaling
        headX *= math.sin(radiansPerPixel * (avg[0] - cwiid.IR_X_MAX / 2.))
        headX *= headDist
        relativeVerticalAngle = radiansPerPixel * (avg[1] - cwiid.IR_Y_MAX / 2)
        headY = movementScaling
        headY *= math.sin(relativeVerticalAngle + cameraVerticalAngle)
        headY *= headDist
        if cameraIsAboveScreen: 
            headY += 0.5
        else:
            headY -= 0.5

        send_socket("%.3f e1 + %.3f e2 + %.3f e3" % (headX, headY, headDist))

#callback_IR = callback_IR_default
#callback_BTN = callback_BTN_default
callback_BTN = callback_track_BTN
callback_IR = callback_track_IR

if __name__ == "__main__":
    main()
