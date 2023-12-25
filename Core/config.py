import configparser
import os
from . import device

class Data:
    """
    Data class with pre-defined default values

    """
    # Default values
    device_model = "DHT11"
    pin = 4
    allow_txt = False
    allow_xl = False
    allow_img = False
    delay_sec = 5
    allow_pulseio = True
    reset_data = False
    select_theme = 0
    temperature_unit = "C"
    graph_environment = "Temperature"
    graph_show = "Both"
    # Default filenames
    txt_filename = "T_and_H.txt"
    xl_filename = "T_and_H.xlsx"
    img_filename = "T_and_H.png"    
    
    def update_from_list(self, data_list):
        self.device_model, self.pin, self.allow_txt, self.allow_xl, self.allow_img, self.delay_sec, self.allow_pulseio, self.reset_data, self.select_theme, self.temperature_unit, self.graph_environment, self.graph_show, self.txt_filename, self.xl_filename, self.img_filename = data_list

    def get_device_class(self):
        return device.convert_name(self.device_model)

class ProgramData:
    """
    Data class with pre-defined default values for temporary files and program settings
    """
    tmp_folderpath  = "Tmp/"
    xl_tmp_filename = "xl_tmp"
    img_tmp_filename = "img_tmp"
    devices = [None,"DHT11","DHT21","DHT22"]
    tmp_device_model = None
    tmp_first_pin = 0
    tmp_last_pin = 20
    tmp_pulseio = True
    tmp_pin = 0
    tmp_found_device = False
    tmp_max_value = 0
    tmp_enable_gui = False
    tmp_scan_all_pins = False
    tmp_current_delay_sec = 0
    tmp_delay_sec = 0

def create(data):
    """
    Creates/updates config file
    Returns:
        Bool: True when a file was created
    """
    config_file = 'dhtreader.ini'
    # Create a ConfigParser object
    config = configparser.ConfigParser()
        
    config['dhtreader'] = {
            'DeviceModel':data.device_model,
            'Pin':data.pin,
            'SaveDataInTxt':data.allow_txt,
            'RecordToExcel':data.allow_xl,
            'CreateImage':data.allow_img,
            'DelayTime':data.delay_sec,
            'UsePulseio':data.allow_pulseio,
            'ResetData':data.reset_data,
            'Theme':data.select_theme,
            'TemperatureUnit':data.temperature_unit,
            'GraphEnviroment':data.graph_environment,
            'TxtFilename':data.txt_filename,
            'ExcelFilename':data.xl_filename,
            'ImageFilename':data.img_filename
    }

    with open(config_file, 'w') as file:
        config.write(file)
    return True

def check():
    """
    Check if config file exists

    Returns:
        boolean: if config file doesn't exist return False, else True
    """
    config_file = 'dhtreader.ini'
    try:
        open(config_file, 'r')
        if os.path.getsize(config_file) <= 1:
            print(f"Config file {config_file} is empty, using default values")
            return False
        return True
    except:
        print(f"Config file {config_file} doesn't exist, using default values")
        return False


def read(data):
    """
    Read config file

    Args:
        data (object): Object with data 

    Raises:
        SystemExit: If config file has an error

    Returns:
        Boolean: True when scan is done
    """
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    config_file = 'dhtreader.ini'
    try:
        # Read the configuration file
        config.read(config_file)
        # Access the values
        data.device_model = config.get('dhtreader','DeviceModel')
        data.pin = config.getint('dhtreader','Pin')
        data.allow_txt = config.getboolean('dhtreader', 'SaveDataInTxt')
        data.allow_xl = config.getboolean('dhtreader', 'RecordToExcel')
        data.allow_img = config.getboolean('dhtreader','CreateImage')
        data.delay_sec = config.getint('dhtreader', 'DelayTime')
        data.allow_pulseio = config.getboolean('dhtreader','UsePulseio')
        data.reset_data = config.getboolean('dhtreader','resetdata')
        data.select_theme = config.get('dhtreader','Theme')
        data.temperature_unit = config.get('dhtreader','TemperatureUnit')
        data.graph_environment = config.get('dhtreader','GraphEnviroment')
        data.txt_filename = config.get('dhtreader','TxtFilename')
        data.xl_filename = config.get('dhtreader','ExcelFilename')
        data.img_filename = config.get('dhtreader','ImageFilename')
                
        return True
    except configparser.Error as e:
        raise SystemExit(f"Error reading config file! {e}")
    