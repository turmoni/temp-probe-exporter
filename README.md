# temp-probe-exporter
Code I use to read temperature data from 1-Wire temperature sensors and spit it out as Prometheus metrics, with a snappy name.

There (are|will be) two core pieces here:
* An Arduino sketch to query sensors
* A Python Prometheus exporter for sensor data, either from an Arduino, or running directly on a Raspberry Pi

## Using with an Arduino
The Arduino sketch cycles through all connected temperature sensors and writes their values out via the serial port, in the form of:

```SENSOR_ID:Temp(C)```

To attach 1-Wire sensors to the Arduino, simply do the following:
* Put a 4.7k resistor between +5v and your data pin (2 by default)
* Attach the data wire from your sensor(s) to the data pin (obviously can be via a breadboard or similar)
* Attach the other two wires to GND

To test that it's working, attach to the serial port exposed by the Arduino. It should be printing out temperature readings.

If you don't know your sensor IDs (a 16-character hexadecimal string), either try them one at a time, or heat/cool one at a time and make a note of which changes.

This is then read by the exporter. Simply \<whatever I actually do when I extend it to support a Pi\>.

## Using with a Raspberry Pi (Zero W)

I don't have mine yet.
