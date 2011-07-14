#!/usr/bin/env python
import cwiid
import numpy
import socket
import sys

COLOR = ["cyan", "magenta", "yellow", "red", "green", "blue", "black", "white"]
point = dict()

def init(sock):
    wiimote_count = int(raw_input("How many Wii Remotes to connect? "))
    wiimotes = list()
    for wiimote_nr in range(wiimote_count):
        raw_input("Put Wii Remote #%d in discovery mode, and press enter. " % wiimote_nr + 1)
        wiimote = cwiid.Wiimote()
        wiimote.led = wiimote_nr + 1
        wiimote.rpt_mode = cwiid.RPT_BTN ^ cwiid.RPT_IR
        wiimote.enable(cwiid.FLAG_MESG_IFC)
        wiimote.mesg_callback = f(wiimote, wiimote_nr, sock)
        wiimotes.append(wiimote)
        point[wiimote] = numpy.array((0, 0))
    print "Connected!"
    return wiimotes

track = [False, False]
track = [True, True]
def f(wiimote, wm_id, sock):
    point_pos = "%(x).3f e1 - %(y).3f e2"
    GAVIEWER_MESG = "p%d = %s(c3ga_point(%s)),$" \
            % (wm_id, COLOR[wm_id % len(COLOR)], point_pos)
    def x(mesgs, t):
        for mesg in filter(None, mesgs):
            if mesg[0] == cwiid.MESG_BTN:
                if cwiid.BTN_B & mesg[1]:
                    print "Start tracking!"
                    wiimote.rpt_mode = cwiid.RPT_BTN ^ cwiid.RPT_IR
                    #track[wm_id] = True
                else:
                    print "End tracking"
                    wiimote.rpt_mode = cwiid.RPT_BTN
                    #track[wm_id] = False
            elif mesg[0] == cwiid.MESG_IR and track[wm_id]:
                blobs = filter(None, mesg[1])
                if blobs:
                    pos_x = -2 * (blobs[0]["pos"][0] - 512) / 1024.
                    pos_y = 2 * (blobs[0]["pos"][1] - 384) / 768.
                    point[wiimote] = numpy.array((pos_x, pos_y))
                    sock.send(GAVIEWER_MESG % {"x": pos_x, "y": pos_y})
    return x

def connect_ga():
    try:
        return socket.create_connection(("localhost", 6860))
    except:
        raw_input("Start GAViewer. and type \"add_net_port(6860)\". Then, press enter in this window.")
        return socket.create_connection(("localhost", 6860))

if __name__ == "__main__":
    sock = connect_ga()
    wms = init(sock)
    exit = False
    while not exit:
        c = sys.stdin.read(1)
        if c == 'q' or c == 'Q':
            exit = True
    for wm in wms:
        wm.close()
