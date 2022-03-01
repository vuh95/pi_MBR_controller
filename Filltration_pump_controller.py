#!/usr/bin/env python3
#Set target flowrate
targetFlow = 26 #ml/min

#Set GPIO
Filtration_pump_pin = 13 
Discharge_pump_pin = 19

#Set up PID parameter
PWM = 25
P = 0.35
I = 0.01
D = 0.05

error_count = 0

#Set up scale date file, output file and time format
import os
scale_port = '/dev/ttyUSB0'
OUTPUTPATH = './data/MBR_Flowrate.csv'
TIMEFORMAT = "%Y/%m/%d %H:%M:%S"

#GPIO configaration
from distutils.log import error
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(Filtration_pump_pin, GPIO.OUT)
Filtration_pump = GPIO.PWM(Filtration_pump_pin, 1000)
Filtration_pump.start(0)
GPIO.setup(Discharge_pump_pin, GPIO.OUT)              
GPIO.output(Discharge_pump_pin, 0)

#Set up PID controller
from simple_pid import PID
pid = PID(P, I, D, setpoint=targetFlow)
pid.output_limits = (-5, 5)

import time
import csv
from datetime import datetime

import serial

class mySerial(serial.Serial):
    # varible to store lines
    buf: bytes = b""
    last_line: str = ""
    delim: bytes = b'\r\n'

    def getLastLine(self):
        # read new data into buf
        self.buf = self.buf + self.read(self.in_waiting)
        
        if (self.buf.count(self.delim) < 3):
            time.sleep(0.01)
            return self.getLastLine()

        if self.delim in self.buf:
            # split data into array of lines
            lines = self.buf.split(self.delim)
            # store uncompleted line into buf
            self.buf = lines[-1]
            # store last line into last_line
            self.last_line = lines[-2].decode()
            #self.reset_input_buffer()
        return self.last_line

Scale_serial = mySerial(
            port = scale_port,
            baudrate = 2400,
            parity = serial.PARITY_EVEN,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.SEVENBITS,
            timeout = None,
            )

def get_scale_value():
    data = Scale_serial.getLastLine()
    data = data.split(",")[1].split(" ")[0]
    data = data.replace('\x00', '')
    data = float (data)
    
    return data
    
Filtration_pump.ChangeDutyCycle(PWM)
time.sleep (1)
start_time = time.time()
last_time = start_time
last_weight = get_scale_value() 
time.sleep (5)

while True:

    try:
        #Get time and weight data
        current_weight = get_scale_value()
        current_time = time.time()
        now = datetime.now().strftime(TIMEFORMAT)
        if current_weight > 3500:
            GPIO.output(Discharge_pump_pin, 1)
            Filtration_pump.ChangeDutyCycle(0)
            time.sleep (10)
            GPIO.output(Discharge_pump_pin, 0)
            time_count = 0
            flowrate_now = 0
            current_time = time.time()
            current_weight = get_scale_value()
        
        #Time in a cycle (sec)
        time_count = round (current_time - start_time, 0)
        
        #Reset time count if over 10 min (600 sec)
        if time_count >= 600:
            start_time = current_time
            time_count = 0
            PWM = 0.85 * PWM
        
        #Caculate flowrate
        flowrate_now = ((current_weight - last_weight) *60 / (current_time - last_time))

        if time_count < 15:
            Filtration_pump.ChangeDutyCycle(PWM)
            pid.reset()

        elif time_count >= 480:
            
            Filtration_pump.ChangeDutyCycle(0)
            
            if time_count > 500 and time_count < 520:
                GPIO.output(Discharge_pump_pin, 1)
                Discharging = True

            else:
                GPIO.output(Discharge_pump_pin, 0)
                Discharging = False

        else:
            
            if flowrate_now < 0:
                pid_feed = 0
            
            else:
                pid_feed = flowrate_now

            pwm_corr = pid(pid_feed)
            PWM += pwm_corr
            
            if PWM > 99:
                PWM = 99
            
            elif PWM < 15:
                PWM = 0

            Filtration_pump.ChangeDutyCycle(PWM)
            
        if time_count >= 490:
            flowrate = 0
        
        else:
            flowrate = flowrate_now
        
        p, i, d = pid.components

        f = open(OUTPUTPATH, 'a', newline='')
        csv.writer(f).writerow([now] + [current_weight] + [flowrate_now] + [flowrate])
        f.close()
        print("{:>5.1f}\t{:>5.1f}\t{:>5.1f}\t{:>5.1f}".format(time_count,flowrate_now, current_weight, PWM))

        last_time = current_time
        last_weight = current_weight
        
        time.sleep(10 - time.time() % 10)
    
    except Exception as EXC:
        print (EXC)
        error_count += 1
        continue

    if error_count > 5:
        break
print ("STOPED")
Filtration_pump.ChangeDutyCycle(0)