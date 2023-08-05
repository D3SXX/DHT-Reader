==============
DHT-Reader
==============

A Python program for scanning and analyzing data from DHT11, DHT21, and DHT22 sensors. The program can record data in text, Excel, and PNG image formats.

Introduction
------------

DHT-Reader is a Python program that allows you to read data from DHT11, DHT21, and DHT22 temperature-humidity sensors and save it into various formats. This program utilizes the `Adafruit_CircuitPython_DHT <https://github.com/adafruit/Adafruit_CircuitPython_DHT>`_ library for sensor communication, `matplotlib <https://github.com/matplotlib/matplotlib>`_ for generating graphs, and `XlsxWriter <https://github.com/jmcnamara/XlsxWriter>`_ for creating Excel files.

Requirements
------------

To use DHT-Reader, you will need the following:

- Raspberry Pi (supported models: Raspberry Pi 4 (tested), Raspberry Pi 3 Model B/B+, Raspberry Pi 2 Model B, Raspberry Pi Model B+, Raspberry Pi Zero)
- DHT11, DHT21, or DHT22 temperature-humidity sensor

Usage
-----

1. Visit the `releases page <https://github.com/D3SXX/DHT-Reader/releases>`_ to find the latest version.
2. Download the preferred one and run it.

- There are 2 versions of the program that are maintained - DHT-Reader and DHT-Reader-GUI
- The main difference between both versions is that DHT-Reader-GUI uses Tkinter to draw a Graphical interface, while DHT-Reader uses Command-Line curses

Building
--------

Dependencies
------------

- Python 3 (tested on Python 3.9.2)

DHT-Reader depends on the following Python libraries:

- `Adafruit_CircuitPython_DHT <https://github.com/adafruit/Adafruit_CircuitPython_DHT>`_
- `matplotlib <https://github.com/matplotlib/matplotlib>`_
- `XlsxWriter <https://github.com/jmcnamara/XlsxWriter>`_

For building use `pyinstaller <https://github.com/pyinstaller/pyinstaller>`_

Follow the instructions below to build DHT-Reader:

1. Install the DHT sensor library by following the instructions in `Adafruit_CircuitPython_DHT repository <https://github.com/adafruit/Adafruit_CircuitPython_DHT>`_.

2. Install the required Python dependencies using pip3:

.. code-block:: shell

    pip3 install adafruit_blinka adafruit-circuitpython-dht matplotlib xlsxwriter pyinstaller

3. Clone/Download the repository.

.. code-block:: shell

    git clone https://github.com/D3SXX/DHT-Reader.git

4. Build the desired program

- To build DHT-Reader.py
.. code-block:: shell

    pyinstaller --onefile --add-binary "/usr/local/lib/python3.9/dist-packages/adafruit_blinka/microcontroller/bcm283x/pulseio/libgpiod_pulsein64:adafruit_blinka/microcontroller/bcm283x/pulseio/" DHT-Reader.py

- To build DHT-Reader-GUI.py

.. code-block:: shell

    pyinstaller --onefile --add-binary "/usr/local/lib/python3.9/dist-packages/adafruit_blinka/microcontroller/bcm283x/pulseio/libgpiod_pulsein64:adafruit_blinka/microcontroller/bcm283x/pulseio/" --hidden-import='PIL._tkinter_finder'  DHT-Reader_Tkinter.py


5. Go to the dist folder

.. code-block:: shell

    cd dist

6. Launch the executable

- To launch DHT-Reader

.. code-block:: shell

    ./DHT-Reader

- To launch DHT-Reader-GUI

.. code-block:: shell

    ./DHT-Reader-GUI
