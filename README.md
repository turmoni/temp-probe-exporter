# temp-probe-exporter
Code I use to read temperature data from 1-Wire temperature sensors and spit it out as Prometheus
metrics, with a snappy name.

There are two core pieces here:
* An Arduino sketch to query sensors
* A Python Prometheus exporter for sensor data, either from an Arduino, or running directly on a
  Raspberry Pi
** This has been tested with Python 2.7 (w1) and 3.6 (serial), requires yaml and pyserial

Note that I am assuming familiarity with Prometheus, learning how to configure it is outside of the
scope of this project (but isn't all that difficult to do for a trivial configuration).

## Hardware setup

### Using with an Arduino
The Arduino sketch cycles through all connected temperature sensors and writes their values out via
the serial port, in the form of:

```SENSOR_ID:Temp(C)```

To attach 1-Wire sensors to the Arduino, simply do the following:
* Put a 4.7k resistor between +5v and your data pin (2 by default)
* Attach the data wire from your sensor(s) to the data pin (obviously can be via a breadboard or
  similar)
* Attach the other two wires to GND

If you want to use a different data pin or change the precision, then this can be changed via
```#define```s at the top of the file. Also, if you want to try using more than 20 sensors (note:
the most I've attempted is 2) then you'll need to make the ```probes``` array bigger.

To test that it's working, attach to the serial port exposed by the Arduino. It should be printing
out temperature readings.

If you don't know your sensor IDs (a 16-character hexadecimal string), either try them one at a
time, or heat/cool one at a time and make a note of which changes.

### Using with a Raspberry Pi (Zero W)

As with the Arduino:
* Hook up a 4.7k resistor between +5v and your data pin (BCM4 by default, see
  https://pinout.xyz/pinout/1_wire for details)
* Attach the data wire from your sensor(s) to the data pin
* Attach the other two wires to GND

You will also need to add the following to /boot/config.txt:

```dtoverlay=w1-gpio,pullup=on```

On powering up your Pi with the sensors connected, you should find /sys/bus/w1/devices/ is
populated. To get the device ID of a given entry, run:

```hd /sys/bus/w1/devices/<device>/id```

To test the temperature sensing:

```cat /sys/bus/w1/devices/<device>/w1_slave```

This will output two lines. The temperature is at the end of the second line, in millidegrees C.
If this doesn't look right, you may need to find out why.

## Using the exporter

The exporter is configured via a (fairly simple) YAML file. An example is provided.

You will need to set sensor_mappings to match your set of sensors. This is a dictionary of
(uppercase) sensor ID to location mappings. The locations are used in a Prometheus label.

You will probably also need to configure the access to the temperature sensor. For a serial
connection to an Arduino, set ```method``` to ```serial```, and ```serial_port``` to your serial
device. For a direct Linux setup (e.g. a Raspberry Pi), simply set ```method``` to ```w1```.

Finally, the default port is 8104, in order to avoid clashing with real exporters by real people.
If you want to change it, set ```exporter_port```.

Simply run the exporter as ```/path/to/prometheus_exporter.py /path/to/prometheus_exporter.yaml```.
A systemd unit file is also provided. The process does not daemonise.

## Notes

Yes, the metric name is terrible and lacks flexibility (onewire_temperature_c). I am sure in the
future I'll have a non-onewire device using the same metric name and I will curse myself.

The code is probably terrible, it has been quickly thrown together for something that works,
because it is hot right now and I want to be able to graph that.
