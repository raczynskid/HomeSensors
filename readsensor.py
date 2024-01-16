#!/usr/bin/env python3

import time
import dbmanager
import huesensors
from bme280 import BME280
from datetime import datetime

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus

import logging

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


bus = SMBus(1)
bme280 = BME280(i2c_dev=bus)

# Tuning factor for compensation. Decrease this number to adjust the
# temperature down, and increase to adjust up
factor = 2.25

# Get the temperature of the CPU for compensation
def get_cpu_temperature():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = f.read()
        temp = int(temp) / 1000.0
    return temp

def get_compensated_temperature(factor: float):
    cpu_temps = [get_cpu_temperature()] * 5
    cpu_temp = get_cpu_temperature()
    # Smooth out with some averaging to decrease jitter
    cpu_temps = cpu_temps[1:] + [cpu_temp]
    avg_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
    raw_temp = bme280.get_temperature()
    comp_temp = raw_temp - ((avg_cpu_temp - raw_temp) / factor)
    return comp_temp

def read_all_sensors(factor: float):
    bathroom_temp, closet_temp, staircase_temp = huesensors.get_hue_sensor_readings()
    for _ in range(3):
        livingroom_temp = get_compensated_temperature(factor)
        humidity = bme280.get_humidity()
        pressure = bme280.get_pressure()
        time.sleep(0.1)
    return(livingroom_temp, bathroom_temp, closet_temp, staircase_temp, humidity, pressure, datetime.now())


db_file = 'enviro.db'
conn = dbmanager.create_connection(db_file)

with conn:
    record = read_all_sensors(factor)
    dbmanager.create_record(conn, record)

conn.close()

logging.info(f'added new record on {datetime.now().strftime("%c")}')
