import cwiid
import socket

def init(s):
    print "Connect to first Wii Remote. " +\
            "Press the 1+2 button on the Wii Remote, and then press enter."
    w1 = cwiid.Wiimote()
    w1.led = cwiid.LED1_ON
    w1.rpt_mode = cwiid.RPT_IR
    w1.enable(cwiid.FLAG_MESG_IFC)
    w1.mesg_callback = f(1, s)
    print "Connect to the second Wii Remote. " +\
            "Press the 1+2 buttons on the Wii Remote, and then press enter."
    w2 = cwiid.Wiimote()
    w2.led = cwiid.LED2_ON
    w2.rpt_mode = cwiid.RPT_IR
    w2.enable(cwiid.FLAG_MESG_IFC)
    w2.mesg_callback = f(2, None)

    return w1, w2

def f(n, s):
    def x(ms, t):
        for m in filter(None, ms):
            if m[0] == 3:
                y = filter(None, m[1])
                if y:
                    print y
                    if s:
                        print y[0]["pos"]
                        print (type(y[0]["pos"][0]), type(y[0]["pos"][1]))
                        T1 = "(1 + %.3f e1 ni)" % (y[0]["pos"][0] / 1024.)
                        T2 = "(1 + %.3f e2 ni)" % (y[0]["pos"][1] / 768.)
                        s.send("cyan(%s %s no ~%s ~%s),$" % (T1, T2, T2, T1))
                    print str(n) + "<" + ",".join([str(x["pos"]) for x in y]) + ">"
    return x

def connect_ga():
    print "Start GAViewer. and type \"add_net_port(6860)\"."
    s = socket.create_connection(("localhost", 6860))
    return s

s = connect_ga()
w1, w2 = init(s)
