#!/usr/bin/env python
"""First scripted tryout with Nao.  The robot will move its head up and down
repeatedly, and do something funky with its ear leds.

Can be called from the command line with one argument, the robot's IP.

"""
import thread
import time

#import set_path

try:
    import naoqi
except ImportError:
    print "No naoqi found!"
    exit(1)

def light_rotor(nao_ip="localhost", nao_port=9559):
    """Lets the LEDs in Nao's ears seem to rotate.

    It can be stopped by setting ALMemory's "User/Ear/LightRotor" value to 0.
    """
    left_ear_led = "Ears/Led/Left/%sDeg/Actuator/Value"
    right_ear_led = "Ears/Led/Right/%sDeg/Actuator/Value"
    rotation_speed = 0.5
    degree_first = 0
    degree_last = 108
    degree_step = 36
    # Setting the ALMemory slot so this function can be stopped from another
    # method.
    memory = naoqi.ALProxy("ALMemory", nao_ip, nao_port)
    memory_name = "User/Ear/LightRotor"
    memory.insertData(memory_name, rotation_speed)
    # Saving the LED statuses to reset when the rotor has stopped
    leds = naoqi.ALProxy("ALLeds", nao_ip, nao_port)
    #old_ear_leds = leds.getIntensity("EarLeds")
    leds.off("EarLeds")
    # Initializing ear LEDs
    # "+ 1" is a  hack to include the led corresponding to degree_last
    for degree in xrange(degree_first, degree_last + 1, degree_step):
        leds.on(left_ear_led % str(degree))
        leds.on(right_ear_led % str(degree))
    # Here the real rotationg starts
    while rotation_speed:
        pids = [\
         leds.post.fade(left_ear_led % str(degree_first), 
             1, rotation_speed),
         leds.post.fade(right_ear_led % str(degree_first), 
             1, rotation_speed),
         leds.post.fade(left_ear_led % str(degree_last), 
             0, rotation_speed),
         leds.post.fade(right_ear_led % str(degree_last), 
             0, rotation_speed)
        ]
        for pid in pids:
            leds.wait(pid, 0)
	degree_first = (degree_first - degree_step) % 360
        degree_last = (degree_last - degree_step) % 360
        rotation_speed = memory.getData(memory_name)
    # Cleanup behaviour
    leds.off("EarLeds")
    #leds.setIntensity("EarLeds", old_ear_leds)

def head_movement(nao_ip="localhost", nao_port=9559):
    """Makes the head nod and shake.

    Can be stopped by setting the "User/Head/Shaker" slot of ALMemory to 0.

    """
    memory = naoqi.ALProxy("ALMemory", nao_ip, nao_port)
    motion = naoqi.ALProxy("ALMotion", nao_ip, nao_port)
    motion.setStiffnesses("Head", 1)
    actuators = ["HeadYaw", "HeadPitch"]
    memory_name = "User/Head/Shaker"
    change_speed = 0.5
    memory.insertData(memory_name, change_speed)
    yaw_rad = [-0.75, 0.75]
    pitch_rad = [-0.3, 0.3]
    i = 0
    while memory.getData("User/Head/Shaker"):
        i += 1
        yaw_pid = motion.angleInterpolation("HeadYaw", yaw_rad[i%2],
                                                 change_speed, True)
        pitch_pid = motion.angleInterpolation("HeadPitch", pitch_rad[i%2],
                                                   change_speed, True)
        """
        for pid in [yaw_pid, pitch_pid]:
            motion.wait(pid, 0)
        time.sleep(change_speed)
        """
    # Cleanup time!
    motion.setStiffnesses("Head", 0)

def main(nao_ip="localhost", nao_port=9559):
    thread.start_new_thread(light_rotor, (nao_ip, nao_port))
    thread.start_new_thread(head_movement, (nao_ip, nao_port))
    # still have to add some stop behaviour...

def stop_all(nao_ip="localhost", nao_port=9559):
    memory = naoqi.ALProxy("ALMemory", nao_ip, nao_port)
    memory.insertData("User/Ear/LightRotor", 0)
    memory.insertData("User/Head/Shaker", 0)

if __name__ == "__main__":
    main()
