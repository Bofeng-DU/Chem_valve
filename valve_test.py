from ChemputerAPI import ChemputerValve
import threading
import logging
import time
import os
import sys

# not sure if you need this, this class is bound with Chemputer and give some info about every step it make
# for example : error cleared
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s ; %(levelname)s ; %(message)s")

def valve_config(valve_adress, *valve_name):
    valve = ChemputerValve(valve_adress, valve_name)
    valve.write_default_valve_configuration()  # write a default configuration to the device and return an confirmation
    # that the config write was successful
    valve.clear_errors()  # clear the previous error
    valve.read_errors()  # advisable to check if the device is now free of errors

    valve.auto_config()# count magnets and determine the home direction.
    # necessary because valve may not precisely at the centred one position, means need homing operation
    # then will turn two full revolutions, and hopefully report success. See common errors down below
    return valve

def valve_move(position, valve):
    if 1 <= position <= 5:
        #valve = valve_config(valve_adress, valve_name)
        valve.move_home()  # First move is ALWAYS to home. Check if homing works as expected.
        # this move is necessary if not will cause Homing problem!
        # This then sets the flag that the operation has completed.
        valve.wait_until_ready()
        valve.move_to_position(str(position))  # postion only from 0 to 5
        #valve.wait_until_ready()

    elif position == 0:
        #valve = valve_config(valve_adress, valve_name)
        valve.move_home()
        valve.wait_until_ready()
        valve.move_to_position(1)# this move seems very important otherwise moving to 0 will cause an error
        valve.wait_until_ready()
        valve.move_to_position(0)
        #valve.wait_until_ready()

    else:
        print("valve doesn't have a " + str(position))

valve_adress = "192.168.1.26" # this ip-adress is hard coded by provider,
# !!! you can also change it with command "assign_ip_address("new one")"
valve_name = "26 valve" # string name can be defined
valve_26 = valve_config(valve_adress, valve_name)
valve_move(position=4, valve=valve_26)
"""
time.sleep(2)
print("move1 finish")
time.sleep(15)
print("move2 start")
valve_move(position=0, valve=valve_26)
"""

def test_func():
    print ("hallo, i am a test_func")

def fun_timer():
    print('hello timer')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    global timer
    timer = threading.Timer(5.8, fun_timer)
    timer.start()
    """
# call according to clock
timer = threading.Timer(2, fun_timer)
timer.start()
# after 50s stop
time.sleep(50)
timer.cancel()
"""
def cyc_run(duration, interval, func, delay,**kwargs):
    i = 0
    while duration > interval:
        func(**kwargs)
        time.sleep(delay)
        running_time = interval * i
        i = i + 1
        if running_time >= duration or running_time + interval > duration:
            print("test end")
            break
#cyc_run(duration = 10, interval = 3, delay = 2, func = test_func)

# COMMON ERROR:
# * Six positive and zero negative magnets (or the other way around) are found: during assembly, the home magnet was not
#   put in the other way. Replace the magnet on the position labeled "3" with one pointing the other way.
#
# * Six positive and one negative magnets (or the other way around) are found: the valve was centred on one position
#   prior to calling auto_config(), and this position is counted twice. This happens sometimes. Move the valve between
#   two positions, write the default config again, and run auto_config() once more.
#
# * Fewer than six magnets (in total) are found: Either a magnet is physically missing (check the valve), or one or more
#   magnets are too weak (demagnetisation due to shock or impact, production fault, etc.). Manually move the valve from
#   position to position, and call read_ADC(). "Negative" magnets should read below 1700, "positive" magnets above 2800.
#   If no faulty magnet can be identified, it's likely a problem with the Hall sensor.
#
# * More than six magnets (in total) are found: This is almost always a faulty Hall effect sensor.
#
# * The correct total amount is detected, but more than one is "the other way around": That's pretty clear, someone
#   cocked up the assembly. Use read_ADC(), another magnet, or a magnet polarity indicator to work out the wrong magnets
#   and replace them.
