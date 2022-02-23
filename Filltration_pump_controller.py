#!/usr/bin/env python3
#Set target flowrate
targetFlow = 40 #ml/min

#Set GPIO
Filtration_pump_pin = 13 
Discharge_pump_pin = 11

#Set up PID parameter
PWM = 50
P = 0.30
I = 0.000
D = 0.05


#Set up scale date file, output file and time format
scale_port = '/dev/ttyUSB0'
OUTPUTPATH = 'MBR_Flowrate.csv'
TIMEFORMAT = "%Y/%m/%d %H:%M:%S"

#GPIO configaration
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
pid.output_limits = (-25, 25)

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
        if (self.buf.count(self.delim) < 2):
            time.sleep(0.01)
            return self.getLastLine()

        if self.delim in self.buf:
            # split data into array of lines
            lines = self.buf.split(self.delim)
            # store uncompleted line into buf
            self.buf = lines[-1]
            # store last line into last_line
            self.last_line = lines[-2].decode()
        return self.last_line

def get_scale_value():
    data = mySerial(
        port = scale_port,
        baudrate = 2400,
        parity = serial.PARITY_EVEN,
        stopbits = serial.STOPBITS_ONE,
        bytesize = serial.SEVENBITS,
        timeout = None,
    ).getLastLine()
    data = data[4:12]
    data = float ("".join(data[0]))
    return data

start_time = time.time()
Filtration_pump.ChangeDutyCycle(50)
time.sleep(5)
last_time = time.time()
last_weight = get_scale_value() 
time.sleep(5)

while True:

    try:
        #Get time and weight data
        current_time = time.time()
        current_weight = get_scale_value()
        if current_weight > 3500:
            GPIO.output(Discharge_pump_pin, 1)
            Filtration_pump.ChangeDutyCycle(0)
            time.sleep (15)
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
        
        #Caculate flowrate
        flowrate_now = ((current_weight - last_weight) *60 / (current_time - last_time))

        if time_count < 10:
            Filtration_pump.ChangeDutyCycle(PWM)
            pid.reset()

        elif time_count >= 480:
            
            Filtration_pump.ChangeDutyCycle(0)
            
            if Discharging_start_time - current_time > 15:
                GPIO.output(Discharge_pump_pin, 0)
                Discharging = False

            if current_weight > 2500 and time_count > 500:
                GPIO.output(Discharge_pump_pin, 1)
                Discharging = True
                Discharging_start_time = current_time

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
        
        now = datetime.now().strftime(TIMEFORMAT)
        if any(d for d in [current_time]):
            f = open(OUTPUTPATH, 'a', newline='')
            csv.writer(f).writerow([now] + [current_weight] + [flowrate_now] + [flowrate])
            f.close()
            print('time in min',"{:.1f}".format((current_weight - start_time)/60))  
            print ('flow', "{:.1f}".format(flowrate_now))
        
        last_time = current_time
        last_weight = current_weight
        
        time.sleep(5 - time.time() % 5)
    
    except Exception as EXC:
        print (EXC)