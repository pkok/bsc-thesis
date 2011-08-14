import threading

# TODO: What's up with exit()? It seems to wait until all non-main threads
# have finished, and then starts calling atexit functions... 



class Callback(threading.Thread):
    def __init__(self, caller):
        threading.Thread.__init__(self, name="Callback for '%s'" % str(caller))
        self.caller = caller
        self.callback_counter = 0
        self.callback_functions = dict()
        self.alive = True

    def terminate(self):
        self.alive = False

    def register(self, callback_fn):
        if hasattr(callback_fn, '__iter__'):
            return map(self.register, callback_fn)

        self.callback_counter += 1
        self.callback_functions[self.callback_counter] = callback_fn
        return self.callback_counter

    def unregister(self, callback_id):
        if callback_id in self.callback_functions:
            del self.callback_functions[callback_id]

    def notify(self, mesg):
        for function in self.callback_functions.values():
            if self.alive:
                function(self.caller, mesg)
            else:
                return

    def run(self):
        previous_timestamp = 0
        while self.alive:
            mesg = self.caller.mesg
            if mesg[0] > previous_timestamp:
                self.notify(mesg)
            previous_timestamp = mesg[0]



# TESTING!
class WiimoteCallback(Callback):
    def __init__(self, wiimote):
        Callback.__init__(self, wiimote)

    def register(self, callback_fn):
        if hasattr(callback_fn, 'require'):
            self.caller.rpt_mode ^= callback_fn.require
        return Callback.register(self, callback_fn)



# FIXME Seems broken. Don't know what goes wrong, actually. When connecting
# through wiimote.Wiimote, the LEDs keep blinking.
class PatternRumbler(threading.Thread):
    def __init__(self, wiimote):
        threading.Thread.__init__(self)
        self.wiimote = wiimote
        self.pattern = []
        self.repeat = True
        self.alive = True
        self.keep_pattern = True

    def terminate(self):
        self.alive = False
        self.keep_pattern = False

    def stop(self):
        return self.set_pattern([], True)

    def set_pattern(self, pattern, repeat=False):
        self.pattern = pattern
        self.repeat = repeat
        self.keep_pattern = False

    def one_repeat(self):
        for duration in self.pattern:
            if not self.alive or not self.keep_pattern:
                self.keep_pattern = True
                return False
            time.sleep(duration)
            self.wiimote.rumble = not self.wiimote.rumble
        return False

    def run(self):
        while self.alive:
            if not self.one_repeat() or not self.repeat:
                if self.keep_pattern:
                    self.pattern = []
                    self.wiimote.rumble = False
