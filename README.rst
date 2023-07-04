==============
DHT-Reader
==============

A Python program for scanning and analyzing data from DHT11, DHT21, and DHT22 sensors. The program can record data into a text file, Excel file, and a PNG image.

Introduction
------------

DHT-Reader is a Python program that allows you to read data from DHT11, DHT21, and DHT22 temperature-humidity sensors and save it into various formats. This program utilizes the `Adafruit_CircuitPython_DHT <https://github.com/adafruit/Adafruit_CircuitPython_DHT>`_ library for sensor communication, `matplotlib <https://github.com/matplotlib/matplotlib>`_ for generating graphs, and `XlsxWriter <https://github.com/jmcnamara/XlsxWriter>`_ for creating Excel files.

Requirements
------------

To use DHT-Reader, you will need the following:

- Raspberry Pi (supported models: Raspberry Pi 4 (tested), Raspberry Pi 3 Model B/B+, Raspberry Pi 2 Model B, Raspberry Pi Model B+, Raspberry Pi Zero)
- DHT11, DHT21, or DHT22 temperature-humidity sensor

Dependencies
------------

DHT-Reader depends on the following Python libraries:

- `Adafruit_CircuitPython_DHT <https://github.com/adafruit/Adafruit_CircuitPython_DHT>`
- `matplotlib <https://github.com/matplotlib/matplotlib>`
- `XlsxWriter <https://github.com/jmcnamara/XlsxWriter>`

You can install these dependencies using pip3:

.. code-block:: shell

    pip3 install matplotlib xlsxwriter

To install the dependencies system-wide, use the following command:

.. code-block:: shell

    sudo pip3 install matplotlib xlsxwriter

Usage
-----

Follow the instructions below to use DHT-Reader:

1. Install the DHT sensor library by following the instructions in `Adafruit_CircuitPython_DHT repository <https://github.com/adafruit/Adafruit_CircuitPython_DHT>`_.

2. Install the required Python dependencies using pip3:

.. code-block:: shell

    pip3 install matplotlib xlsxwriter

3. Fetch the latest version of DHT-Reader.py from the releases.

4. On the first startup, the program will ask whether to create a new config file ('dhtreader.ini'). You can choose 'y' for yes or 'n' for no. If you select 'n' or just press Enter, default values will be used.

5. Run the program and start reading data from the DHT sensor.
