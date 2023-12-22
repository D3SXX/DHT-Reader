import adafruit_dht
import board
from . import config

def convert_name(device):
    if device == "DHT11":
        return adafruit_dht.DHT11
    elif device == "DHT22":
        return adafruit_dht.DHT22
    elif device == "DHT21":
        return adafruit_dht.DHT21
    elif device == adafruit_dht.DHT11:
        return "DHT11"
    elif device == adafruit_dht.DHT22:
        return "DHT22"
    elif device == adafruit_dht.DHT21:
        return "DHT21"
    else:
        raise SystemExit("Something went wrong, check your config file!\nUnknown device " + str(device)) 

def init(data):
    print(data.get_device_class(),data.pin, data.allow_pulseio)
    # Initial the dht device, with data pin connected to:
    device = data.get_device_class()
    pin_value = getattr(board, "D" + str(data.pin))
    dht_device = device(pin_value, data.allow_pulseio)
    print(f"Device {data.device_model} with pin {data.pin} initialized\nPulseio is set to {data.allow_pulseio}")
    return dht_device
def stop(dhtDevice):
    dhtDevice.exit()
    print("dhtDevice stop")

def re_init(data = None,dhtDevice = None, device_model = None, pin = None, allow_pulseio = None):
    stop(dhtDevice)
    if not data:
        new_data = config.Data()
        new_data.device_model = device_model
        new_data.pin = pin
        new_data.allow_pulseio = allow_pulseio
        return init(new_data)
    return init(data)

def get_data(dht_device):
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        return temperature, humidity
    except RuntimeError as error:
        # Handle errors
        return False,error.args[0]