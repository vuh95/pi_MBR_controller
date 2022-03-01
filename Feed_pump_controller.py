#!/usr/bin/env python
#set GPIO pin
Scale_pin = [18,15]
Feed_pump_pin = 26 

Scale_offset = -21200
Scale_ratio = 58.08

import RPi.GPIO as GPIO  # import GPIO
from hx711 import HX711  # import the class HX711
import pandas as pd
import numpy as np
import os
import csv
from datetime import datetime
import time

try:
    GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
    # Create an object hx which represents your real hx711 chip
    # Required input parameters are only 'dout_pin' and 'pd_sck_pin'
    scale = HX711(dout_pin=Scale_pin[0], pd_sck_pin=Scale_pin[1])
    scale.set_offset(int(Scale_offset))
    scale.set_scale_ratio(int(Scale_ratio))

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Feed_pump_pin, GPIO.OUT)
    GPIO.setup(Feed_pump_pin, GPIO.OUT)
    GPIO.output(Feed_pump_pin, 0)

except Exception as ee:
    print (ee)
    print ("error")

def get_value():
    value = scale.get_weight_mean(2)
    if value != False:
        return value
    else:
        return 0

OUTPUTPATH = './data/data_scale.csv'
TIMEFORMAT = "%Y/%m/%d %H:%M:%S"

#error_count = 0
while True:
    try:
        now = datetime.now().strftime(TIMEFORMAT)
        Scale_value = []
        for i in range (2):
            Scale_value.append(get_value())
            time.sleep (0.2)
            
        Scale_value_std = np.std(Scale_value)
        Scale_value_mean = np.mean(Scale_value)

        if Scale_value_std > 10:
            continue

        if Scale_value_mean < 15850:
                GPIO.output(Feed_pump_pin, 1)
        
        if Scale_value_mean > 16100:
                GPIO.output(Feed_pump_pin, 0)

        f = open(OUTPUTPATH, 'a', newline='')
        csv.writer(f).writerow([now] + [Scale_value_mean])
        f.close()
        print("{:>5}\t{:>5.1f}\t{:>5.1f}".format(now, Scale_value_mean, Scale_value_std))
        time.sleep(10 - time.time() % 10)
    except KeyboardInterrupt:
        GPIO.output(Feed_pump_pin, 0)
        break
    except Exception as EXC:
        print (EXC)
        



