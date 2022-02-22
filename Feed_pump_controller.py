#!/usr/bin/env python
#set tank scale pin
tank_scale_pin = [4,17]

#
import RPi.GPIO as GPIO  # import GPIO
from hx711 import HX711  # import the class HX711
import pandas as pd
import numpy as np
import os
import csv
import threading
from datetime import datetime
import time
try:
    cal_data = pd.read_csv("/home/pi/MBR/Data/cal_scale.csv")
    cal_data_1 = cal_data.query ( "scale == 1")
    cal_data_2 = cal_data.query ( "scale == 2")
    cal_value_1 = cal_data_1.iloc[-1]
    cal_value_2 = cal_data_2.iloc[-1]
    print ("oK")
except Exception as ee:
    print (ee)
    print ("cant get cal data from csv file")

try:
    GPIO.setmode(GPIO.BCM)  # set GPIO pin mode to BCM numbering
    # Create an object hx which represents your real hx711 chip
    # Required input parameters are only 'dout_pin' and 'pd_sck_pin'
    hx1 = HX711(dout_pin=5, pd_sck_pin=6)
    hx2 = HX711(dout_pin=23, pd_sck_pin=24)
    hx1.set_offset(int(cal_value_1["offset"]))
    hx1.set_scale_ratio(int(cal_value_1["ratio"]))
    hx2.set_offset(int(cal_value_2["offset"]))
    hx2.set_scale_ratio(int(cal_value_2["ratio"]))
except Exception as ee:
    print (ee)
    print ("error")


def get_value(scale_no):
    if scale_no == 1:
        value_1 = hx1.get_weight_mean(15)
        if value_1 != False:
            value1.append (round(value_1,0))
        else:
            value1.append ("")
    elif scale_no == 2:
        value_2 = hx2.get_weight_mean(15)
        if value_2 != False:
            value2.append (round(value_2,0))
        else:
            value2.append ("")
    else:
        asadasd = 8/0

OUTPUTPATH = '/home/pi/MBR/Data/data_scale.csv'
TIMEFORMAT = "%Y/%m/%d %H:%M:%S"
csv_data = []
try:
    while True:
        value1 =[]
        value2 =[]
        now = datetime.now().strftime(TIMEFORMAT)
        t1 = threading.Thread(target=get_value, args=(1,))
        t2 = threading.Thread(target=get_value, args=(2,))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        print (value1, value2)
        f = open(OUTPUTPATH, 'a', newline='')
        csv.writer(f).writerow([now] + value1 + value2)
        f.close()
        time.sleep(5 - time.time() % 5)
except Exception as ee:
    print (ee)
    print ("error")
finally:
    GPIO.cleanup()
    print("clean")
