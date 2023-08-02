#DHT Reader v0.29 by D3SXX

try:
    import os
    import time
    from datetime import datetime
    import configparser
    import board
    import adafruit_dht
    import matplotlib.pyplot as plt
    import xlsxwriter
    import argparse
    import shutil
    import curses
except:
    raise SystemExit("Some dependencies are missing. Please run the following command to install them:\npip3 install adafruit_blinka adafruit-circuitpython-dht matplotlib xlsxwriter")

# Reset array and add save any sentences
def save_and_reset_array(array, sentences_to_save=1):
    array_length = len(array)
    if array_length > sentences_to_save:
        array_to_save = array[array_length - sentences_to_save:]
        array.clear()
        array.extend(array_to_save)
        
# A converter for dht name
# Also if flag is set to 1 it checks for correct name
def dht_convert(device, flag=None):
    if device == "DHT11":
        if flag == 1:
            raise Exception("Something went wrong, is there enough entries in your config file?")
        return adafruit_dht.DHT11
    elif device == "DHT22":
        if flag == 1:
            raise Exception("Something went wrong, is there enough entries in your config file?")     
        return adafruit_dht.DHT22
    elif device == "DHT21":
        if flag == 1:
            raise Exception("Something went wrong, is there enough entries in your config file?")
        return adafruit_dht.DHT21
    elif device == adafruit_dht.DHT11:
        return "DHT11"
    elif device == adafruit_dht.DHT22:
        return "DHT22"
    elif device == adafruit_dht.DHT21:
        return "DHT21"
    else:
        raise SystemExit("Something went wrong, check your config file!\nUnknown device " + str(device)) 

# Reads or writes to/from the config file, depends on flag
def read_and_write_config(flag, select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename,excel_filename, img_filename):
    
    config_file = 'dhtreader.ini'
    
    if flag == 1:
        
        # Create a ConfigParser object
        config = configparser.ConfigParser()
        
        device = dht_convert(device)
        
        config['dhtreader'] = {
            'DeviceModel':device,
            'Pin':pin,
            'SaveDataInTxt':allowtxt,
            'RecordToExcel':allowxl,
            'CreateImage':allowimg,
            'DelayTime':delay_sec,
            'UsePulseio':allow_pulseio,
            'ResetData':reset_data,
            'Theme':select_theme,
            'TemperatureUnit':temperature_unit,
            'GraphEnviroment':graph_environment,
            'TxtFilename':txt_filename,
            'ExcelFilename':excel_filename,
            'ImageFilename':img_filename
        }

        with open(config_file, 'w') as file:
            config.write(file)
        return True
    else:
        # Create a ConfigParser object
        config = configparser.ConfigParser()

        try:
            # Check if config file is empty
            try:
                open(config_file, 'r')
                if os.path.getsize(config_file) <= 1:
                    print(f"Config file {config_file} is empty, using default values")
                    return select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename  
            except:
                print(f"Config file {config_file} doesn't exist, using default values")
                return select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename  
            
            # Read the configuration file
            config.read(config_file)

            # Access the values
            device = config.get('dhtreader','DeviceModel')
            pin = config.get('dhtreader','Pin')
            allowtxt = config.getint('dhtreader', 'SaveDataInTxt')
            allowxl = config.getint('dhtreader', 'RecordToExcel')
            allowimg = config.getint('dhtreader','CreateImage')
            delay_sec = config.getint('dhtreader', 'DelayTime')
            allow_pulseio = config.getint('dhtreader','UsePulseio')
            reset_data = config.getint('dhtreader','resetdata')
            select_theme = config.getint('dhtreader','Theme')
            temperature_unit = config.get('dhtreader','TemperatureUnit')
            graph_environment = config.get('dhtreader','GraphEnviroment')
            txt_filename = config.get('dhtreader','TxtFilename')
            excel_filename = config.get('dhtreader','ExcelFilename')
            img_filename = config.get('dhtreader','ImageFilename')
                
            # Convert "device" from str to appropriate type
            device = dht_convert(device)
            return select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename   
        except configparser.Error as e:
            raise SystemExit(f"Error reading config file! {e}")

# Create an Excel file and an Image
def write_to_xl(temperature, humidity,excel_filename, img_filename, flag):
    # flag == 1 -> allow only xl, flag == 2 allow only image, flag == 3 allow both
    return_list = []
    
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
    df = [date_time, temperature, humidity]

    # Check if 'xl_tmp' temporary file exists, create it if not
    try:
        with open("xl_tmp", "a") as f:
            f.write("\n" + " ".join(str(x) for x in df))
    except FileNotFoundError:
        with open("xl_tmp", "w") as f:
            f.write(" ".join(str(x) for x in df))

    # Read the contents of 'xl_tmp' file
    with open("xl_tmp", "r") as f:
        tmp_xl = f.readlines()

    a = len(tmp_xl)
    
    stroftime = []
    strofT = []
    strofH = []
    
    # Process each line in 'xl_tmp' and extract date, time, temperature, and humidity
    for entry in tmp_xl:
        data = entry.split()
        if len(data) >= 3:  # Check if line has expected number of elements
            stroftime.append(data[0] + " " + data[1])  # Combine date and time
            strofT.append(data[2])
            strofH.append(data[3])

    if flag == 2 or flag == 3:
        start_time = time.time()
        # Plot the humidity and temperature data
        
        # Create a figure and axis objects
        fig, ax = plt.subplots()
    
        # Generate dynamic x values based on stroftime length
        x = range(len(stroftime))
    
        # Plot temperature line
        ax.plot(x, strofT, label='Temperature')
        # Plot humidity line
        ax.plot(x, strofH, label='Humidity')
        # Add labels and legend
        ax.set_xlabel('Amount of reads')
        ax.legend()
        plt.savefig(img_filename, dpi=300, bbox_inches='tight')
        full_time = time.time() - start_time
        img_size = os.path.getsize(img_filename)
        return_list.append(f"An image {img_filename} ({img_size} bytes) was created in {full_time:.2f} seconds")
        if flag == 2:
            return return_list

    # Create an Excel workbook and worksheet
    
    workbook = xlsxwriter.Workbook(excel_filename, {'strings_to_numbers': True})
    worksheet = workbook.add_worksheet()
    datetime_format = workbook.add_format({'num_format': 'dd/mm/yyyy, hh:mm:ss'})
    number_format = workbook.add_format({'num_format': '0'})

    stroflegend = ['Date and Time', 'Temperature', 'Humidity']
    for col_num, data in enumerate(stroflegend):
        worksheet.write(0, col_num, data)

    # Write the data to the worksheet
    for row_num, data in enumerate(stroftime):
        worksheet.write(row_num + 1, 0, data, datetime_format)

    for row_num, data in enumerate(strofT):
        worksheet.write(row_num + 1, 1, int(data), number_format)

    for row_num, data in enumerate(strofH):
        worksheet.write(row_num + 1, 2, int(data), number_format)

    # Create charts for temperature and humidity
    chart = workbook.add_chart({'type': 'line'})
    chart.add_series({'values': '=Sheet1!$B$2:$B$%d' % a})
    chart.set_title({"name": "Temperature"})
    worksheet.insert_chart('E1', chart)

    chart2 = workbook.add_chart({'type': 'line'})
    chart2.add_series({'values': '=Sheet1!$C$2:$C$%d' % a})
    chart2.set_title({"name": "Humidity"})
    worksheet.insert_chart('E17', chart2)

    # Close the workbook
    workbook.close()
    xl_size = os.path.getsize(excel_filename)
    return_list.append(f"An Excel file {excel_filename} ({xl_size} bytes) with {a} entries was created")
    
    return return_list 

#Creare a txt file    
def write_to_txt(temperature, humidity, txt_filename):

    # Record data in a text file
    with open(txt_filename, "a") as f:
        # Check what is the time right now
        now = datetime.now()
        # Format it for better readability
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        # Make a structure that holds all the data
        entry = f"{date_time} Temperature: {temperature} Humidity: {humidity}\n"
        # Write this structure to a file
        f.write(entry)
    txt_size = os.path.getsize(txt_filename)
    
    return [str(f"{txt_filename} ({txt_size} bytes) file was updated ")]


def main(stdscr):
    
    parser = argparse.ArgumentParser(description='A DHT-Reader CLI Interface')
    parser.add_argument('--skip', action='store_true', help='Skip config check')
    parser.add_argument('--debug', action='store_true', help='Show debug info')
    parser.add_argument('--autodetect', action='store_true', help='Auto detect device')    
    args = parser.parse_args()
    
    # Default values
    allowtxt = 0
    allowxl = 0
    allowimg = 0
    delay_sec = 5
    allow_pulseio = 1
    reset_data = 0
    device = dht_convert("DHT11")
    pin = board.D4
    select_theme = 0
    temperature_unit = "C"
    graph_environment = "Temperature"
    
    # Default filenames
    txt_filename = "T_and_H.txt"
    excel_filename = "T_and_H.xlsx"
    img_filename = "T_and_H.png"
    
    
    debug_msg = ""
    ascii_logo = '''
 __  _  _ _____   ___ ___  __  __  ___ ___  
| _\| || |_   _| | _ | __|/  \| _\| __| _ \ 
| v | >< | | |   | v | _|| /\ | v | _|| v / 
|__/|_||_| |_|   |_|_|___|_||_|__/|___|_|_\\ 
'''
    
    # Set up the window
    curses.curs_set(0)  # Hide the cursor
    stdscr.nodelay(1)  # Non-blocking input
    stdscr.timeout(1000)  # Refresh rate (milliseconds)
    
    # Init colors
    curses.start_color()
    curses.use_default_colors()
    
    
    
    class WindowData:
        def __init__(self, width, height):
            
            top_window_y = 4
            bottom_window_y = top_window_y + height // 2
            box_width_right = width*55//100+1
            box_width_left = width-box_width_right-3 # Leave some space for graph numbers
            box_height_top = int(height*0.5)
            if args.debug:
                box_height_bottom = int(height-box_height_top-top_window_y-3) # Add additional space for debug info
            else:
                box_height_bottom = int(height-box_height_top-top_window_y-2)
            
            self.window_data = {
                'window1': {
                    'box_x': 0,
                    'box_y': top_window_y,
                    'box_width': box_width_right,  # Should always connect to the graph box
                    'box_height': box_height_top
                },
                'window2': {
                    'box_x': width*55//100,
                    'box_y': top_window_y,
                    'box_width': box_width_left,
                    'box_height': box_height_top
                },
                'window4': {
                    'box_x': width*55//100,
                    'box_y': bottom_window_y,
                    'box_width': box_width_left,
                    'box_height': box_height_bottom 
                },
                'window3': {
                    'box_x': 0,
                    'box_y': bottom_window_y,
                    'box_width': box_width_right,
                    'box_height': box_height_bottom 
                }
            }

        def get_window_coordinates(self, window_name):
            if window_name in self.window_data:
                return tuple(self.window_data[window_name].values())
            else:
                raise ValueError(f"Window '{window_name}' does not exist.")
    
    def auto_detect(flag = 0, scan_all = 1, first_pin = 0, last_pin = 20):
        global dhtDevice
        logs_list = []
        pin = 0
        allow_pulseio = 1
        y = 0
        height, width = stdscr.getmaxyx()
        devices = ["DHT11","DHT21","DHT22"]
        if flag == 1:
            if last_pin >= 7 and last_pin < 8:
                cut_val = 6
            elif last_pin >= 8:
                cut_val = 12
            else:
                cut_val = 0
            if first_pin > 0:
                val = first_pin
            else:
                val = 0
            progress_bar = 0
            max_value_pg = (last_pin+1-first_pin)*3*2-cut_val+val
        for current_device in devices:
            msg = f"Checking the {current_device}"
            if flag != 1:
                stdscr.addstr(y, 0, msg,curses.A_BOLD)
                stdscr.refresh()
                y += 1
            else:
                logs_list.append(msg)
            device = dht_convert(current_device) # maybe remove
            for allow_pulseio in range(1,-1,-1):
                msg = f"Pulseio is set to {bool(allow_pulseio)}"
                if flag != 1:
                    stdscr.addstr(y, 0, msg,curses.A_BOLD)
                    stdscr.refresh()
                    y += 1
                else:
                    logs_list.append(msg)
                for pin in range(first_pin,last_pin+1):
                    try:
                        if pin == 7 or pin == 8:
                            continue
                        if flag == 1:
                            dhtDevice.exit()
                        pin_value = getattr(board, "D" + str(pin))
                        dhtDevice = device(pin_value, bool(allow_pulseio))
                        msg = f"Checking pin {pin}"
                        if flag != 1:
                            if y+3 >= height:
                                y=0
                                stdscr.clear()
                            stdscr.addstr(y, 0, msg,curses.A_BOLD)
                            stdscr.refresh()
                            y += 1
                        else:
                            logs_list.append(msg)
                            progress_bar += 1
                        temperature = dhtDevice.temperature
                        humidity = dhtDevice.humidity
                        if flag != 1:
                                stdscr.addstr(y, 0, f"{temperature},{humidity}",curses.A_BOLD)
                                stdscr.refresh()
                                y += 1
                        else:
                            logs_list.append(f"{temperature},{humidity}")
                        msg = f"Detected {current_device} at pin {pin} (Pulseio is set to {bool(allow_pulseio)})"
                        if flag != 1:
                            stdscr.addstr(y, 0, msg,curses.A_BOLD)
                            stdscr.refresh()
                            time.sleep(2)
                            y += 1
                        else:
                            logs_list.append(msg)
                            if scan_all != 0:
                                progress_bar = max_value_pg
                        if scan_all == 0:
                            return 0
                    except RuntimeError as error:
                        if str(error) == "DHT sensor not found, check wiring":
                            dhtDevice.exit()
                            if flag == 1:
                                print(f"Error: {error}")
                            else:
                                logs_list.append(error)
                        else:
                            if flag == 1:
                                print(f"Error: {error}")
                            else:
                                logs_list.append(error)
                            msg = f"Detected {current_device} at pin {pin} (Pulseio is set to {bool(allow_pulseio)})"
                            if flag != 1:
                                stdscr.addstr(y, 0, msg,curses.A_BOLD)
                                stdscr.refresh()
                                time.sleep(1)
                                y += 1
                            else:
                                logs_list.append(msg)
                            if scan_all != 0:
                                progress_bar = max_value_pg
                            if scan_all == 0:
                                return 0
    
    def cli_check_config_file():
        config_file = 'dhtreader.ini'
        if not os.path.isfile(config_file):
            while True:
                create_new_config = [f"Config file '{config_file}' does not exist.","Do you want to create a new config file? (y/n): "]
                stdscr.clear()
                height, width = stdscr.getmaxyx()
                draw_box(0, 0, width-1, height-1)
                for i, value in enumerate(create_new_config):
                    stdscr.addstr(i+1,1,value)
                    
                # Get user input
                key = stdscr.getch()
                
                if key == ord('y') or key == ord('Y'):
                    return "Create"
                elif key == ord('n') or key == ord('N'):
                    return False
                stdscr.refresh()
        else:
            return True
            
    def cli_delay(time_sec, x, y):
        while time_sec >= 1:
            delay_text = f"The next reset will be in {time_sec} seconds"
            stdscr.addstr(y, x, delay_text)
            stdscr.refresh()
            time.sleep(1)
            time_sec -= 1 
    
    def draw_box(box_y, box_x, box_width, box_height):
        
        # Turn on color pair to color the box
        stdscr.attron(curses.color_pair(2))
        # Draw the horizontal lines
        stdscr.addstr(box_y, box_x, '+' + '-' * (box_width - 2) + '+')  # Top border
        stdscr.addstr(box_y + box_height, box_x, '+' + '-' * (box_width - 2) + '+')  # Bottom border

        # Draw the vertical lines
        for y in range(box_y + 1, box_y + box_height):
            stdscr.addstr(y, box_x, '|')  # Left border
            stdscr.addstr(y, box_x + box_width - 1, '|')  # Right border
        
        #Turn off color pair
        stdscr.attroff(curses.color_pair(2))
        
    def cli_draw_interface():
        
        # Set up the info box
        
        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window1')  
                        
        # Draw box
                    
        draw_box(box_y, box_x, box_width, box_height)
        
        # Set up the graph box
        
        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window2') 
        # Set up the graph
        graph_x = box_x + 1
        graph_x_axis = box_height // 2 + box_y

        # Draw box 
                    
        draw_box(box_y, box_x, box_width, box_height)
        
        # Set up error messages box
        
        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window4')  
        # Draw box
                    
        draw_box(box_y, box_x, box_width, box_height)

        
        # Set up logs box
        
        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window3')

        # Draw box
        
        draw_box(box_y, box_x, box_width, box_height)
   
    def cli_top_bar():
        # Draw top bar
                    
        now = datetime.now()  
        current_time = "Current time: " + now.strftime("%d/%m/%Y, %H:%M:%S") + " Next update: T-" + str(i)  

        clock_x = (width - len(current_time)) // 2
        clock_y = 0
                    
        # Draw the clock
        
        stdscr.addstr(clock_y, clock_x, current_time, curses.A_BOLD)
        
        # Add some icons on the top bar to indicate various things
                    
        icon_x = clock_x + len(current_time) + 2
                    
        if error_happen == 1:
            stdscr.addstr(clock_y, icon_x, "E",curses.color_pair(4) | curses.A_BOLD)
        if i <= 1:
            stdscr.addstr(clock_y, icon_x+2, "R",curses.color_pair(5) | curses.A_BOLD)
        if args.debug:
            stdscr.addstr(clock_y, icon_x+4, "D",curses.color_pair(6) | curses.A_BOLD)
        # Draw a line
        y_line = 1
                    
        stdscr.addstr(y_line, 0, "-" * width, curses.color_pair(2) | curses.A_BOLD)
                
    def cli_read_config():
        
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        window_info = WindowData(width, height)
        
        y = 0
        list_delay = 0.3 # Change to make listing longer or faster 
        txt_mode = "ON"
        xl_mode = "ON"
        img_mode = "ON"
        reset_data_mode = "NOT RESET"
        pulseio_mode = "ENABLED"
        if allowtxt == 0:
            txt_mode = "OFF"
        if allowxl == 0:
            xl_mode = "OFF"
        if allowimg == 0:
            img_mode = "OFF"
        if reset_data == 1:
            reset_data_mode = "RESET"
        if allow_pulseio == 0:
            pulseio_mode = "DISABLED"
        
        
        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window3')
        logs.append("Using " + dht_convert(device,1))
        logs.append("Using pin " + str(pin))
        logs.append("Writing to an Excel file is " + xl_mode)
        logs.append("Creating a PNG image is " + img_mode)
        logs.append("The delay is set to " + str(delay_sec) + " seconds")
        logs.append("Pulseio is " + pulseio_mode)
        logs.append("The data will be " + reset_data_mode)
        stdscr.addstr(y, 0, logs[0],curses.A_BOLD)
        y += 1 
        stdscr.refresh()
        time.sleep(list_delay)
        stdscr.addstr(y, 0, logs[1],curses.A_BOLD)
        y += 1 
        stdscr.refresh()
        time.sleep(list_delay)
        stdscr.addstr(y, 0, logs[2],curses.A_BOLD)
        y += 1 
        stdscr.refresh()
        time.sleep(list_delay)        
        stdscr.addstr(y, 0, logs[3],curses.A_BOLD)
        y += 1 
        stdscr.refresh()
        time.sleep(list_delay)
        stdscr.addstr(y, 0, logs[4],curses.A_BOLD)
        y += 1 
        stdscr.refresh()
        time.sleep(list_delay)
        stdscr.addstr(y, 0, logs[5],curses.A_BOLD)
        y += 1 
        stdscr.refresh()
        time.sleep(list_delay)
        stdscr.addstr(y, 0, logs[6],curses.A_BOLD)
        y += 1 
        stdscr.refresh()
    
        if reset_data == 1:
            file_names = ["T_and_H.txt", "xl_tmp"]
            for file_name in file_names:
                try:
                    os.remove(file_name)
                    logs.append(f"File '{file_name}' deleted successfully")
                except FileNotFoundError:
                    logs.append(f"File '{file_name}' not found")
                    
                except PermissionError:
                    logs.append(f"Unable to delete file '{file_name}'. Permission denied")
                except Exception as e:
                    logs.append(f"An error occurred while deleting file '{file_name}': {str(e)}")
            stdscr.addstr(y, 0, logs[7],curses.A_BOLD)
            y += 1 
            stdscr.addstr(y, 0, logs[8],curses.A_BOLD)
            stdscr.refresh()
            y += 1
        
        
        stdscr.addstr(y, 0, ascii_logo,curses.A_BOLD)
        y += 6
        stdscr.refresh()
        cli_delay(3, 0, y+2)
    
    def cli_debug(debug_msg = ""):
        debug_str=f"Width: {width} Height: {height} " + str(debug_msg)
        stdscr.addstr(height-1, 0, debug_str, curses.A_BOLD)

    def cli_bottom_bar(debug_msg):
        
        # Get coordinates
        bottom_x = 0
        bottom_y = height - 1
        
        # Check if debug argument is present and draw debug info
        if args.debug:
            cli_debug(debug_msg)
            bottom_y -= 1
        
        # Draw bottom bar
        bottom_msg = "Press Q to (Q)uit | S to open (S)ettings | C to (C)hange graph | T to skip delay"
        # cut is used to remove letters when the width is smaller than the string
        cut = len(bottom_msg)
        if len(bottom_msg) > width:
            cut = len(bottom_msg) - (len(bottom_msg) - width)
            
        stdscr.addstr(bottom_y, bottom_x,bottom_msg[:cut], curses.A_BOLD)
    
    def cli_info_box(xl_info_amount):
        
        # Set up the info box
        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window1')
                    
        # Draw info
                    
        lower_y = box_y + 1
        lower_x = box_x + 1
                    
        # Draw box and title
        box_name = "Information"
                                                       
        # Calculate the x-coordinate to center the text
                                    
        text_x = box_x + box_width // 2 - len(box_name) // 2 
        stdscr.addstr(box_y-1, text_x, box_name, curses.A_BOLD)
                    
        # Turn on color pair to color the text in the info box
        stdscr.attron(curses.color_pair(3))
                    
        stdscr.addstr(lower_y, lower_x, "Model: " + dht_convert(device))
        lower_y += 1
        stdscr.addstr(lower_y, lower_x, "Pin: " + str(pin))
        lower_y += 1
        stdscr.addstr(lower_y, lower_x, f"Temperature: {str(temperature)} °{temperature_unit}")
        
        lower_y += 1
        stdscr.addstr(lower_y, lower_x, "Humidity: " + str(humidity) + "%" )
        lower_y += 1
        stdscr.addstr(lower_y, lower_x, "Sensor delay: " + f"{time_took:.3f} Seconds")
        
        # Add additional information about Excel and image
        msg_2 = None      
        for msg in info_xl:
            xl_info_amount += 1
            # Check if the info message is bigger than the width of the box and add \n to conpensate
            if len(msg) > box_width-3:
                msg_2 = msg[box_width-3:]
                msg = msg[:box_width-3] 
            stdscr.addstr(lower_y+xl_info_amount , lower_x, msg)
            if not msg_2 == None:
                xl_info_amount += 1 
                stdscr.addstr(lower_y+xl_info_amount , lower_x, msg_2) 
    
    def cli_graph_box(environment):
        # Turn on color pair
        stdscr.attron(curses.color_pair(3))

        # Check environment variable and use apropriate data
        
        if environment == "Temperature":
            values = temperature_hold
        else:
            values = humidity_hold

        # Draw graph

        # Set up the graph box

        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window2') 
                        
        # Set up the graph
        graph_x = box_x + 1
        graph_x_axis = box_height // 2 + box_y

        # Draw box and title
        graph_name = environment
                        
                        
        # Calculate the x-coordinate to center the text
        text_x = box_x + box_width // 2 - len(graph_name) // 2 
                        
        stdscr.addstr(box_y-1, text_x, graph_name, curses.A_BOLD)
                        
        # Calculate the scaling factors
        if environment == "Temperature":
            if device == dht_convert("DHT11"):
                max_value = 50
                min_value = 0 # different for each sensor, this one if for DHT11
            elif device == dht_convert("DHT22"):
                max_value = 80
                min_value = 0 # -40 breaks graph, fix required
            else:
                max_value = 80
                min_value = 0
            if temperature_unit == "F":
                max_value = int(1.8 * max_value + 32)
                min_value = int(1.8 * min_value + 32)
        else:
            max_value = 100
            min_value = 0
        
        scale_factor = (max_value-min_value)/(box_height-2)
                    
        # Generate scaled values for demonstration
        scaled_values = [int(scale_factor * value) for value in range(box_height - 2, -1, -1)]
                        
        for y, value in enumerate(scaled_values):
            stdscr.addstr(y + box_y + 1 , box_x + box_width + 1, str(value),curses.A_BOLD)
                        
        # Draw the graph points 
                        
        debug_str = ""
        # Check if list is too big
                        
        if len(values) >= box_width-2:
            save_and_reset_array(values)
                        
        # Draw graph line
        for k, value in enumerate(values):
            x = 1 + k
            for d, value_y in enumerate(scaled_values[::-1]):

                if value >= value_y:
                    y = d
                            
            box_y_start = box_y + box_height
                            
            stdscr.addch(box_y_start-1-y, box_x + x, "•", curses.A_BOLD)

    def cli_error_box(error_msg, errors_amount):
        
        # Set up error messages

        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window4')
                    
        if not error_msg == None:
                        
            # Check if the size of array is bigger than the box
            if len(error_msg) >= box_height-1:
                save_and_reset_array(error_msg)
                            
            # Turn on color pair
            stdscr.attron(curses.color_pair(4))
                        
            msg_2 = None      
            for msg in error_msg:
                errors_amount += 1
                # Check if the error message is bigger than the width of the box and add \n to conpensate
                if len(msg) > box_width-2:
                    msg_2 = msg[box_width-2:]
                    msg = msg[:box_width-2] 
                stdscr.addstr(box_y+errors_amount , box_x+1, msg)
                if not msg_2 == None:
                    errors_amount += 1 
                    if errors_amount >= box_height-1:
                        # Perhaps not the best way to solve the issue of checking if the text will fit on display, but it works
                        error_msg = error_msg + error_msg
                        break
                    stdscr.addstr(box_y+errors_amount , box_x+1, msg_2) 
            stdscr.attroff(curses.color_pair(4))
            return errors_amount 
    
    def cli_logs_box(logs,logs_amount):
        
        # Set up logs.
                    
        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window3')
                     
        if not logs == None:
                        
            # Check if the size of array is bigger than the box
            if len(logs) >= box_height-1:
                save_and_reset_array(logs,box_height-1)
                            
            # Turn on color pair
            stdscr.attron(curses.color_pair(1))
                        
            msg_2 = None      
            for msg in logs:
                logs_amount += 1
                # Check if the error message is bigger than the width of the box and add \n to conpensate
                if len(msg) > box_width-2:
                    msg_2 = msg[box_width-2:]
                    msg = msg[:box_width-2] 
                stdscr.addstr(box_y+logs_amount , box_x+1, msg)
                if not msg_2 == None:
                    logs_amount += 1 
                    if logs_amount >= box_height-1:
                        # Perhaps not the best way to solve the issue of checking if the text will fit on display, but it works
                        logs = logs + logs
                        break
                    stdscr.addstr(box_y+logs_amount , box_x+1, msg_2) 
            stdscr.attroff(curses.color_pair(1))
            return logs_amount
    
    def cli_themes(select = 0):
        # Define color pairs
        
        if select == 0: # Default theme
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # for top clock, logs
            curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # For box borders
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK) # For text, graph
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK) # For error logs, top pannel indication (red)
            curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK) # For top pannel indication (Reset)
            curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK) # For top pannel indication (Debug)
            curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE) # For text highlight
        elif select == 1: # Monochrome
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # for top clock, logs
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK) # For box borders
            curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK) # For text, graph
            curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK) # For error logs, top pannel indication (red)
            curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK) # For top pannel indication (Reset)
            curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK) # For top pannel indication (Debug)
            curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE) # For text highlight
        elif select == 2: # Classic blue
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # for top clock, logs
            curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE) # For box borders
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLUE) # For text, graph
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLUE) # For error logs, top pannel indication (red)
            curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLUE) # For top pannel indication (Reset)
            curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLUE) # For top pannel indication (Debug)
            curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_BLUE) # For text highlight
        elif select == 3: # Inverted monochrome
            curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE) # for top clock, logs
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE) # For box borders
            curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE) # For text, graph
            curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE) # For error logs, top pannel indication (red)
            curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE) # For top pannel indication (Reset)
            curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE) # For top pannel indication (Debug)
            curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_WHITE) # For text highlight
        stdscr.bkgd(' ', curses.color_pair(1) | curses.A_BOLD)
        
    def cli_settings_menu(select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename,excel_filename, img_filename):
        
        # Flag is only changed if configuration was changed
        flag = 0
        
        # Object to hold old values for comparison
        old_values = [select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename]
        
        pos_y = 2
        pos_x = 1
        select = 0
        while True:
            settings = ["Change theme","Change configuration",f"Change temperature unit (°{temperature_unit})" ,"Exit"]
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            draw_box(0, 0, width-1, height-1)
            if args.debug:
                debug_msg_1 = f"width: {width} height: {height} pos_x: {pos_x} pos_y {pos_y} "
                stdscr.addstr(height-2, 1, debug_msg_1, curses.A_BOLD)
            stdscr.addstr(1, 1, "Settings", curses.A_BOLD)
            for i, setting in enumerate(settings):
                if i == pos_y-2:
                    stdscr.addstr(2+i, 1, setting, curses.color_pair(7))
                    select = i
                else:
                    stdscr.addstr(2+i, 1, setting, curses.A_BOLD)
            
            stdscr.addstr(pos_y, pos_x+30, "<--", curses.A_BOLD)
            
            
            # Get user input
            key = stdscr.getch()

            # Exit the loop
            if key == ord('q') or key == ord('Q'):
                new_values = [select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename,excel_filename, img_filename]
                if old_values != new_values:
                    flag = 1
                return select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data,graph_environment, txt_filename,excel_filename, img_filename, flag
            elif key == curses.KEY_UP:
                if pos_y > 2:
                    pos_y -= 1
            elif key == curses.KEY_DOWN:
                if not pos_y > len(settings):
                    pos_y += 1
            elif key == ord('\n'):
                if select == 0:
                    
                    themes = ["   Default >>","<< Monochrome >>","<< Classic Blue >>","<< Inverted monochrome   "]
                    options = ["Select","Exit"]
                    
                    line = 0
                    old_theme = select_theme
                    while True:
                        stdscr.clear()
                        height, width = stdscr.getmaxyx()
                        
                        cli_themes(select_theme)
                        
                        if args.debug:
                            debug_msg_1 = f"width: {width} height: {height} theme: {select_theme}. {(themes[select_theme])[3:-3]} line {line} "
                            stdscr.addstr(height-1, 1, debug_msg_1, curses.A_BOLD)
                        
                        box_width = int(width * 0.4)
                        box_height = int(height * 0.4)
                        draw_box(height//2-(box_height // 2), width//2-(box_width // 2), box_width, box_height)
                        box_title = "Theme selector"
                        box_add = "Press enter to preview"
                        stdscr.addstr(int(height*0.40), width//2-len(box_title)//2,box_title)
                        stdscr.addstr(int(height*0.45), width//2-len(box_add)//2,box_add)
                        if line == 0:
                            stdscr.addstr(height//2, width//2-len(themes[select_theme]) // 2, themes[select_theme], curses.color_pair(7))
                            stdscr.addstr(height//2+int(height*0.1), width//2-int(box_width // 3), options[0], curses.A_BOLD)
                            stdscr.addstr(height//2+int(height*0.1), width//2+int(box_width // 3)-len(options[1]), options[1], curses.A_BOLD)
                        elif line == 1:
                            stdscr.addstr(height//2, width//2-len(themes[select_theme]) // 2, themes[select_theme], curses.A_BOLD)
                            stdscr.addstr(height//2+int(height*0.1), width//2-int(box_width // 3), options[0], curses.color_pair(7))
                            stdscr.addstr(height//2+int(height*0.1), width//2+int(box_width // 3)-len(options[1]), options[1], curses.A_BOLD)
                        elif line == 2:
                            stdscr.addstr(height//2, width//2-len(themes[select_theme]) // 2, themes[select_theme], curses.A_BOLD)
                            stdscr.addstr(height//2+int(height*0.1), width//2-int(box_width // 3), options[0], curses.A_BOLD)
                            stdscr.addstr(height//2+int(height*0.1), width//2+int(box_width // 3)-len(options[1]), options[1], curses.color_pair(7))
                        
                        
                        # Get user input
                        key = stdscr.getch()
                        if key == ord('q') or key == ord('Q'):
                            break
                        elif key == curses.KEY_LEFT:
                            if select_theme > 0 and line == 0:
                                select_theme -= 1
                            elif line == 2 and line > 0:
                                line -= 1
                        elif key == curses.KEY_RIGHT:
                            if select_theme < len(themes)-1 and line == 0:
                                select_theme += 1
                            elif line == 1 and line < 2:
                                line += 1
                        elif key == curses.KEY_UP:
                            if line > 0:
                                line -= 1
                        elif key == curses.KEY_DOWN:
                            if not line > len(options)-2:
                                line += 1
                        elif key == ord('\t'):
                            if line == 0:
                                line = 1
                            else:
                                line = 0
                        elif key == ord('\n'):
                            if line == 1:
                                break
                            elif line == 2:
                                select_theme = old_theme
                                cli_themes(select_theme)
                                break
                            elif line == 0:
                                
                                while True:
                                    stdscr.clear()
                                    height, width = stdscr.getmaxyx()
                                    cli_themes(select_theme)
                                    stdscr.addstr(height-1,0,f"Previewing: {(themes[select_theme])[3:-3]}", curses.color_pair(1))
                                    cli_draw_interface()
                                    cli_top_bar()
                                    window_info = WindowData(width, height)
                                    cli_info_box(xl_info_amount)
                                    box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window4')
                                    stdscr.addstr(box_y+1, box_x+1, "Errors",curses.color_pair(4))
                                    key = stdscr.getch()
                                    
                                    if key == ord('\n') or key == ord('q') or key == ord('Q'):
                                        break
                                    elif key == curses.KEY_LEFT:
                                        if select_theme > 0:
                                            select_theme -= 1
                                    elif key == curses.KEY_RIGHT:
                                        if select_theme < len(themes)-1:
                                            select_theme += 1
                                    stdscr.refresh()
                        stdscr.refresh()
                elif select == 1:
                    options = ["DHT Device","Pin","Save data in txt","Save data to Excel", "Save data to image", "Delay time", "Use pulseio", "Reset data each time","Change txt file name", "Change Excel file name", "Change image file name", "Exit"]
                    line = 0
                    while True:
                        options_parameters = [dht_convert(device),f"D{pin}",bool(allowtxt),bool(allowxl),bool(allowimg),f"{delay_sec} Seconds",bool(allow_pulseio),bool(reset_data), txt_filename, excel_filename, img_filename, ""]
                        
                        stdscr.clear()
                        height, width = stdscr.getmaxyx()
                        draw_box(0, 0, width-1, height-1)
                        
                        for i, value in enumerate(options):
                            if line == i:
                                stdscr.addstr(i+1,1,value, curses.color_pair(7))
                                stdscr.addstr(i+1,40,str(options_parameters[i]), curses.color_pair(7))
                            else:
                                stdscr.addstr(i+1,1,value)
                                stdscr.addstr(i+1,40,str(options_parameters[i]))
                        
                        
                        # Get user input
                        key = stdscr.getch()
                        if key == ord('q') or key == ord('Q'):
                            break
                        elif key == curses.KEY_LEFT:
                            if line == 0:
                                if dht_convert(device) == "DHT22":
                                    device = dht_convert("DHT21")
                                elif dht_convert(device) == "DHT21":
                                    device = dht_convert("DHT11")
                                else:
                                    device = dht_convert("DHT22")
                            elif line == 1:
                                if int(pin) > 0:
                                    pin = int(pin) - 1
                            elif line == 2:
                                allowtxt = int(not bool(allowtxt))
                            elif line == 3:
                                allowxl = int(not bool(allowxl))
                            elif line == 4:
                                allowimg = int(not bool(allowimg))
                            elif line == 5:
                                if delay_sec > 0:
                                    delay_sec -= 1
                            elif line == 6:
                                allow_pulseio = int(not bool(allow_pulseio))
                            elif line == 7:
                                reset_data = int(not bool(reset_data))                                
                                
                        elif key == curses.KEY_RIGHT:
                            if line == 0:
                                if dht_convert(device) == "DHT11":
                                    device = dht_convert("DHT21")
                                elif dht_convert(device) == "DHT21":
                                    device = dht_convert("DHT22")
                                else:
                                    device = dht_convert("DHT11")
                            elif line == 1:
                                if int(pin) < 40:
                                    pin = int(pin) + 1
                            elif line == 2:
                                allowtxt = int(not bool(allowtxt))
                            elif line == 3:
                                allowxl = int(not bool(allowxl))
                            elif line == 4:
                                allowimg = int(not bool(allowimg))
                            elif line == 5:
                                delay_sec += 1
                            elif line == 6:
                                allow_pulseio = int(not bool(allow_pulseio))
                            elif line == 7:
                                reset_data = int(not bool(reset_data))     
                        elif key == curses.KEY_UP:
                            if line > 0:
                                line -= 1
                        elif key == curses.KEY_DOWN:
                            if not line > len(options)-2:
                                line += 1
                        elif key == ord('\t'):
                            if line == 0:
                                line = 1
                            else:
                                line = 0
                        elif key == ord('\n'):
                            if line == len(options)-1:
                                break
                            if line == 0:
                                if dht_convert(device) == "DHT22":
                                    device = dht_convert("DHT21")
                                elif dht_convert(device) == "DHT21":
                                    device = dht_convert("DHT11")
                                else:
                                    device = dht_convert("DHT22")
                            elif line == 1:
                                new_pin = "D"
                                while True:
                                    stdscr.refresh()
                                    stdscr.addstr(line+1,40,f"[{new_pin}]", curses.color_pair(7))
                                    enter = stdscr.getstr().decode()
                                    if enter == "":
                                        break
                                    elif enter.isnumeric():
                                        new_pin += enter
                                        pin = int(enter)
                            elif line == 2:
                                allowtxt = int(not bool(allowtxt))
                            elif line == 3:
                                allowxl = int(not bool(allowxl))
                            elif line == 4:
                                allowimg = int(not bool(allowimg))
                            elif line == 5:
                                new_delay = ""
                                while True:
                                    stdscr.refresh()
                                    stdscr.addstr(line+1,40,f"[{new_delay} Seconds]", curses.color_pair(7))
                                    enter = stdscr.getstr().decode()
                                    if enter == "":
                                        break
                                    elif enter.isnumeric():
                                        new_delay += enter
                                        delay_sec = int(enter)
                            elif line == 6:
                                allow_pulseio = int(not bool(allow_pulseio))
                            elif line == 7:
                                reset_data = int(not bool(reset_data))
                            elif line == 8:
                                new_filename = ""
                                space = ""
                                for i in range(len(txt_filename)-4):
                                    space += " " 
                                while True:
                                    stdscr.refresh()
                                    stdscr.addstr(line+1,40,f"[{space}{new_filename}.txt]", curses.color_pair(7))
                                    enter = stdscr.getstr().decode()
                                    if enter == "":
                                        break
                                    else:
                                        new_filename += enter
                                        txt_filename = enter + ".txt"
                                        space = ""
                            elif line == 9:
                                new_filename = ""
                                space = ""
                                for i in range(len(excel_filename)-5):
                                    space += " " 
                                while True:
                                    stdscr.refresh()
                                    stdscr.addstr(line+1,40,f"[{space}{new_filename}.xlsx]", curses.color_pair(7))
                                    enter = stdscr.getstr().decode()
                                    if enter == "":
                                        break
                                    else:
                                        new_filename += enter
                                        excel_filename = enter + ".xlsx"
                                        space = ""
                            elif line == 10:
                                new_filename = ""
                                space = ""
                                for i in range(len(img_filename)-4):
                                    space += " " 
                                while True:
                                    stdscr.refresh()
                                    stdscr.addstr(line+1,40,f"[{space}{new_filename}.png]", curses.color_pair(7))
                                    enter = stdscr.getstr().decode()
                                    if enter == "":
                                        break
                                    else:
                                        new_filename += enter
                                        img_filename = enter + ".png"
                                        space = ""
                elif select == 2:
                        if temperature_unit == "C":
                            temperature_unit = "F"
                        else:
                            temperature_unit = "C"
                elif select == len(settings)-1:
                    new_values = [select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment,txt_filename, excel_filename, img_filename]
                    if old_values != new_values:
                        flag = 1
                    return select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data,graph_environment, txt_filename, excel_filename, img_filename, flag
                pos_x = 1

            # Refresh the screen
            stdscr.refresh()
    
    # Apply default theme
    cli_themes()
    
    if not args.skip:
        cfg = cli_check_config_file()
        if cfg == "Create":
            select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data,graph_environment, txt_filename,excel_filename, img_filename, flag = cli_settings_menu(select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename,excel_filename, img_filename)
            flag = 1
            read_and_write_config(flag, select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename,excel_filename, img_filename)
        elif cfg == True:
            flag = 2
            select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename = read_and_write_config(flag, select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename,excel_filename, img_filename)
    if args.autodetect:
        auto_detect(0,0)
        global dhtDevice
    else:
        # Initial the dht device, with data pin connected to:
        pin_value = getattr(board, "D" + str(pin))
        dhtDevice = device(pin_value, bool(allow_pulseio))
    # Apply theme from config
    cli_themes(select_theme)
    

    
    # Array for holding temperature and humidity
    temperature_hold = []
    humidity_hold = []

    # Array for holding error messages
    errors_amount = 0
    error_msg = []
    # For topbar indication
    error_happen = 0
    
    # Array for holding text for logs box
    logs_amount = 0
    logs = []
    
    # For graph
    tmp_y = 0
    
    # For info window
    xl_info_amount = 0
    info_xl = []
    
    if not args.skip:
       cli_read_config()
    
    while True:
        try:
            #start_time, end_time and time_took are for calculation the time of delay of a sensor
            humidity, temperature = None, None
            start_time = time.time()
            while humidity == None or temperature == None: #make readings until there are any values
                try:
                    temperature = dhtDevice.temperature
                    humidity = dhtDevice.humidity
                except RuntimeError as error:
                    # Errors happen fairly often, DHT's are hard to read, just keep going
                    
                    # Add new entry to error box
                    error_msg.append(error.args[0])
                    error_happen = 1
                    
                    # Add entry to logs
                    now = datetime.now()
                    logs.append("Error hapenned at " + now.strftime("%d/%m/%Y, %H:%M:%S"))
                    break

            if not temperature == None:
                if temperature_unit == "F":
                    temperature = int(1.8 * temperature + 32)
                temperature_hold.append(temperature)
                humidity_hold.append(humidity)
            end_time = time.time()
            time_took = end_time - start_time

            i = delay_sec
            while i>0:
                    stdscr.clear()

                    height, width = stdscr.getmaxyx()
                    
                    window_info = WindowData(width, height)
                    
                    cli_draw_interface()
                   
                    cli_top_bar()
                    
                    cli_info_box(xl_info_amount)

                    
                    cli_graph_box(graph_environment)
                
                    errors_amount = cli_error_box(error_msg, errors_amount)
                                            
                    logs_amount = cli_logs_box(logs, logs_amount)

                    if args.debug:
                        
                        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window1')
                        debug_msg = f"W1: {box_width}x{box_height} "            
                        
                        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window2')
                        debug_msg = debug_msg + f"W2: {box_width}x{box_height} " 
                
                        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window3')
                        debug_msg = debug_msg + f"W3: {box_width}x{box_height} "
                        
                        box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window4')
                        debug_msg = debug_msg + f"W4: {box_width}x{box_height} "  
   
                    cli_bottom_bar(debug_msg)                            
                        
                    # Get user input
                    key = stdscr.getch()

                    # Exit the loop
                    if key == ord('q') or key == ord('Q'):
                        dhtDevice.exit()
                        return 0
                    elif key == ord('s') or key == ord('S'):
                        flag = 0
                        select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data,graph_environment, txt_filename, excel_filename, img_filename, flag = cli_settings_menu(select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename)
                        if flag == 1:
                            read_and_write_config(flag, select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename)
                            dhtDevice.exit()
                            pin_value = getattr(board, "D" + str(pin))
                            dhtDevice = device(pin_value, bool(allow_pulseio))
                            
                            i = delay_sec
                            logs.append("Configuration was changed")
                    elif key == ord('c') or key == ord('C'):
                        if graph_environment == "Temperature":
                            graph_environment = "Humidity"
                        else:
                            graph_environment = "Temperature"
                    elif key == ord('t') or key == ord('T'):
                        i = 0
                    i -= 1
                    errors_amount = 0
                    xl_info_amount = 0
                    logs_amount = 0
                    
                    # Refresh the screen
                    stdscr.refresh()
            
            error_happen = 0
            info_xl = []
            
            if not temperature == None:
                if allowtxt == 1:
                    info_xl.extend(write_to_txt(temperature,humidity,txt_filename))
                    pass
                if allowxl == 1 or allowimg == 1:
                # flag == 1 -> allow only xl, flag == 2 allow only image, flag == 3 allow both
                    flag = 0
                    if allowxl == 1 and allowimg == 1:
                        flag = 3
                    elif allowxl == 1 and allowimg == 0:
                        flag = 1
                    else:
                        flag = 2
                    info_xl.extend(write_to_xl(temperature,humidity,excel_filename,img_filename,flag))
            
        except Exception as error:
                dhtDevice.exit()
                raise SystemExit(error)
        except KeyboardInterrupt:
                raise SystemExit
    
curses.wrapper(main)
