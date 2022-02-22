import time
import os
import csv
import board
import busio
from datetime import datetime
import pandas as pd
# import adafruit_ads1x15.ads1015 as ADS
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# you can specify an I2C adress 
ads1 = ADS.ADS1115(i2c, address=0x48)
ads2 = ADS.ADS1115(i2c, address=0x49)
ads3 = ADS.ADS1115(i2c, address=0x4A)
ads4 = ADS.ADS1115(i2c, address=0x4B)

# Create single-ended input on channel 0
#chan = AnalogIn(ads, ADS.P0)

# Create differential input between channel 0 and 1
chan11 = AnalogIn(ads1, ADS.P0, ADS.P1)
chan12 = AnalogIn(ads1, ADS.P2, ADS.P3)

chan21 = AnalogIn(ads2, ADS.P0, ADS.P3)
chan22 = AnalogIn(ads2, ADS.P2, ADS.P3)

chan31 = AnalogIn(ads3, ADS.P0, ADS.P3)
chan32 = AnalogIn(ads3, ADS.P2, ADS.P3)

chan41 = AnalogIn(ads4, ADS.P0, ADS.P1)
chan42 = AnalogIn(ads4, ADS.P2, ADS.P3)

OUTPUTPATH = "./Data/adc.csv"
TIMEFORMAT = "%Y/%m/%d %H:%M:%S"
count = 0
check_file = os.path.exists(OUTPUTPATH)
if check_file == False: # Creat file if not exist.
    f = open(OUTPUTPATH, "a", newline="")
    csv.writer(f).writerow(['Time'] +
                            ['DO_1'] + ['Temp_1'] + ['Flow_1'] + ['P_1'] + 
                            ['DO_2'] + ['Temp_1'] + ['Flow_2'] + ['P_2'])
    f.close()
    print ("Output file was created")
    print ("Output file is ready")
else:
    print ("Output file is ready")
while True:
    p1 = chan11.voltage
    p2 = chan41.voltage
    flow_1 = chan12.voltage
    flow_2 = chan42.voltage
    do_1 = chan21.voltage*10/4
    temp_1 = chan22.voltage*50/5
    do_2 = chan31.voltage*10/4
    temp_2 = chan32.voltage*50/5

    now = datetime.now().strftime(TIMEFORMAT)
    f = open(OUTPUTPATH, "a", newline="")
    csv.writer(f).writerow(
                            [now] + 
                            [do_1] + [temp_1] + [flow_1] + [p1]+ 
                            [do_2] + [temp_2] + [flow_2] + [p2])
    f.close()
    df = pd.read_csv(OUTPUTPATH)
    os.system('clear')
    print (df.tail(10))
    time.sleep(5 - time.time() % 5)