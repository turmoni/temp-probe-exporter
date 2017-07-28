#!/usr/bin/env python
# coding=utf8
"""Prometheus monitoring for temperatures via an Arduino"""

from __future__ import print_function

import re
import sys
import os
import time
import serial
import yaml
from prometheus_client import start_http_server, Gauge

def main():
    """Do things with stuff"""
    if len(sys.argv) != 2:
        print('Usage: {0} <config.yaml>'.format(sys.argv[0]))
        sys.exit()

    try:
        conf_file = open(sys.argv[1], 'r')
        conf = yaml.safe_load(conf_file)
    except Exception as e:
        print('Error loading config: {0}'.format(str(e)), file=sys.stderr)

    sensor_mappings = conf.get('sensor_mappings')
    prometheus_port = conf.get('exporter_port', 8104)
    method = conf.get('method')
    onewire_temperature_c = Gauge('onewire_temperature_c', 'Temperature in C', ['location'])

    # Start the prometheus HTTP server
    start_http_server(prometheus_port)

    if method == 'serial':
        read_serial(onewire_temperature_c, sensor_mappings, conf.get('serial_port'))
    elif method == 'w1':
        read_w1(onewire_temperature_c, sensor_mappings)
    else:
        print('Invalid method specified: {0}'.format(method), file=sys.stderr)
        sys.exit()

def read_serial(onewire_temperature_c, sensor_mappings, serial_port):
    """Read data from a serial port"""
    ser = serial.Serial(serial_port, timeout=60)
    while 1:
        line = ser.readline()
        m = re.match(r'([A-Z0-9]{16}):([0-9.]+)\n', line.decode('ascii'))
        if m:
            onewire_temperature_c.labels(location=sensor_mappings[m.group(1)]).set(m.group(2))

def read_w1(onewire_temperature_c, sensor_mappings):
    """Read data from /sys/bus/w1/drivers/w1_slave_driver/"""
    base_dir = '/sys/bus/w1/drivers/w1_slave_driver/'

    # Get our device:
    path_mappings = {}
    for (directory, dirs, files) in os.walk(base_dir):
        for dev_dir in dirs:
            try:
                id_file = open('{0}/{1}/id'.format(base_dir, dev_dir), 'r')
                id_val = id_file.read().encode('hex').upper()
                id_file.close()
                therm_file = open('{0}/{1}/w1_slave'.format(base_dir, dev_dir), 'r')
                path_mappings[id_val] = therm_file
            except (OSError, IOError) as e:
                print('Skipping {0} due to error: {1}'.format(dev_dir, str(e)), file=sys.stderr)
        break

    while 1:
        for device_id, therm_file in path_mappings.items():
            therm_contents = therm_file.read()
            therm_file.seek(0)

            m = re.search(r't=(\d{5})$', therm_contents)
            if m:
                temperature = (float(m.group(1)) / 1000)
                # A reading of 85000 seems to mean "it's not working". If you actually want to
                # measure things that are 85°C, then my apologies.
                if temperature != 85:
                    onewire_temperature_c.labels(location=sensor_mappings[device_id]).set(temperature)

        time.sleep(1)

if __name__ == '__main__':
    main()
