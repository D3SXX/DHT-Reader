#DHT Reader v0.21 beta RC by D3SXX

try:
    import os # consider removing
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
    print("Some dependencies are missing. Please run the following command to install them:")
    print("pip3 install adafruit_blinka adafruit-circuitpython-dht matplotlib xlsxwriter")
    raise SystemExit()

parser = argparse.ArgumentParser(description='A DHT-Reader CLI Interface')
parser.add_argument('--skip', action='store_true', help='Skip config check')
parser.add_argument('--debug', action='store_true', help='Show debug info')


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

# Reset array and add save any sentences
                
def save_and_reset_array(array, sentences_to_save=1):
    array_length = len(array)
    if array_length > sentences_to_save:
        array_to_save = array[array_length - sentences_to_save:]
        array.clear()
        array.extend(array_to_save)
        
        
def highlight_word(word, flag):
    # Set the color based on the input parameter
    if flag == 3:
        color_code = '\033[97m'  # White
    elif flag == 0:
        color_code = '\033[91m'  # Red
    elif flag == 1:
        color_code = '\033[92m'  # Green
    elif flag == 4:
        color_code = '\033[93m'  # Yellow
    else:
        color_code = '\033[0m'  # Default color (no highlighting)
    print(f"{color_code}{word}\033[0m", end="")

def delay_wait(time_s):
    print("\nThe next reset will be in %d" %time_s, end='..', flush=True)
    for i in reversed(range(time_s)):
        print("%d" % i, end= '..', flush=True)
        time.sleep(1)
    print("Resetting!")

# A converter for dht name
# Also if flag is set to 1 it checks for correct name
def dht_convert(device, flag=None):
    if device == "DHT11":
        if flag == 1:
            highlight_word("\nSomething went wrong, is there enough entries in your config file?\n",0)
            raise Exception
        return adafruit_dht.DHT11
    elif device == "DHT22":
        if flag == 1:
            highlight_word("\nSomething went wrong, is there enough entries in your config file?\n",0)
            raise Exception        
        return adafruit_dht.DHT22
    elif device == "DHT21":
        if flag == 1:
            highlight_word("\nSomething went wrong, is there enough entries in your config file?\n",0)
            raise Exception
        return adafruit_dht.DHT21
    elif device == adafruit_dht.DHT11:
        return "DHT11"
    elif device == adafruit_dht.DHT22:
        return "DHT22"
    elif device == adafruit_dht.DHT21:
        return "DHT21"
    else:
        print("Something went wrong, check your config file!")
        raise Exception("Unknown device " + str(device)) 

def scan_config():
    config_file = 'dhtreader.ini'
    device = "DHT11"
    pin = board.D4
    allowtxt = 0
    allowxl = 0
    allowpng = 0
    delay_sec = 5
    reset_data = 0
    allow_pulseio = 1
    if not os.path.isfile(config_file):
        create_new_config = input(f"Config file '{config_file}' does not exist.\nDo you want to create a new config file? (y/n): ")
        if create_new_config.lower() == 'y':
            # Create a new config file
            config = configparser.ConfigParser()
            tmp = 0
            print("Type y or n, or press enter to select the default option")
            while True:
                tmp = str(input("Choose any model of DHT which you would like to read\n1. DHT11\n2. DHT22\n3. DHT21/AM2301\n"))
                if input == '1':
                    break
                elif input == '2':
                    device = "DHT22"
                    break
                elif input == '3':
                    device = "DHT21"
                    break
                else:
                    break
            while True:
                tmp = str(input("Choose any pin\n1. D4\n2. D5\n3. D17\n4. D22\n5. D27\n"))
                if input == '1':
                    break
                elif input == '2':
                    pin = board.D5
                    break
                elif input == '3':
                    pin = board.D17
                    break
                elif input == '4':
                    pin = board.D22
                    break
                elif input == '5':
                    pin = board.D27
                    break
                else:
                    break
                                
            tmp = str(input("Write data in txt file? (default is no)"))
            if tmp.lower() == "y":
                allowtxt = 1
            tmp = str(input("Write data in excel file? (default is no)"))
            if tmp.lower() == "y":
                allowxl = 1
            tmp = input("Make a DHT_Reader.png image with temperature and humidity?")
            if tmp.lower() == "y":
                allowpng = 1
            while True:
                tmp = str(input("Type any delay value in seconds (default is 5)"))
                if tmp == "":
                    break
                elif tmp.isdecimal() == True:
                    if int(tmp) > 0:
                        delay_sec = int(tmp)   
                        break
                else:
                    print("Wrong input! Use any numbers that are greater than 0")
            tmp = input("Use pulseio(Change this option only if you can't read any data, default is yes)")
            if tmp.lower() == "n":
                allow_pulseio = 0
            tmp = str(input("Would you like to reset data every time the program is run?"))
            if tmp.lower() == "y":
                reset_data = 1
            config['dhtreader'] = {
                'DeviceModel':device,
                'Pin':pin,
                'SaveDataInTxt':allowtxt,
                'RecordToExcel':allowxl,
                'CreateImage':allowpng,
                'DelayTime':delay_sec,
                'UsePulseio':allow_pulseio,
                'ResetData':reset_data
            }

            with open(config_file, 'w') as file:
                config.write(file)
            #change device type so the program will work
            device = dht_convert(device)
            print(f"New config file '{config_file}' created.")
        else:
            print("No new config file created, using default values.")
            #change device type so the program will work
            device = dht_convert(device)
    else:
        # Create a ConfigParser object
        config = configparser.ConfigParser()

        try:
            # Read the configuration file
            config.read(config_file)

            # Access the values
            device = config.get('dhtreader','DeviceModel')
            pin = config.get('dhtreader','Pin')
            allowtxt = config.getint('dhtreader', 'SaveDataInTxt')
            allowxl = config.getint('dhtreader', 'RecordToExcel')
            allowpng = config.getint('dhtreader','CreateImage')
            delay_sec = config.getint('dhtreader', 'DelayTime')
            allow_pulseio = config.getint('dhtreader','UsePulseio')
            reset_data = config.getint('dhtreader','resetdata')
                
            # Convert "device" from str to appropriate type
            device = dht_convert(device)
                    
        except configparser.Error as e:
            print(f"Error reading the config file: {e}")
    return allowtxt, allowxl, allowpng, delay_sec, allow_pulseio, reset_data, device, pin


# Create an Excel file and an Image.
def write_to_xl(temperature, humidity, flag):
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
        img_name = "DHT_Reader.png"
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
        plt.savefig(img_name, dpi=300, bbox_inches='tight')
        full_time = time.time() - start_time
        img_size = os.path.getsize(img_name)
        return_list.append(f"An image {img_name} ({img_size} bytes) was created in {full_time:.2f} seconds")
        if flag == 2:
            return return_list

    # Create an Excel workbook and worksheet
    return_list.append(f"An Excel file with {a} entries was created")
    workbook = xlsxwriter.Workbook('T_and_H.xlsx', {'strings_to_numbers': True})
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
    return return_list 
    
def write_to_txt(temperature, humidity):
    # Record data in a text file
    with open("T_and_H.txt", "a") as f:
        # Check what is the time right now
        now = datetime.now()
        # Format it for better readability
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        # Make a structure that holds all the data
        entry = f"{date_time} Temperature: {temperature} Humidity: {humidity}\n"
        # Write this structure to a file
        f.write(entry)

    print(f"\nThe data that was added to the T_and_H.txt:\n{date_time} Temperature: {temperature} Humidity: {humidity}")


# Temporary solution for holding default values here
args = parser.parse_args()
allowtxt = 0
allowxl = 0
allowimg = 0
delay_sec = 5
allow_pulseio = 1
reset_data = 0
device = dht_convert("DHT11")
pin = board.D4


if not args.skip:
    allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, data_reset, device, pin = scan_config()
 

def main(stdscr):
    
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
    
    # Define color pairs
   # curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # White and black
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Purple and black
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK) # Green and black
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK) # Red and black
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK) # Blue and black
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Yellow and black
    stdscr.bkgd(' ', curses.color_pair(1) | curses.A_BOLD)
    
    
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
        bottom_x = 0
        bottom_y = height - 1
        if args.debug:
            cli_debug(debug_msg)
            bottom_y -= 1
        bottom_msg = "Press Q to (Q)uit | S to open (S)ettings | C to (C)hange graph"
        stdscr.addstr(bottom_y, bottom_x,bottom_msg, curses.A_BOLD)
    
    def cli_settings_menu():
        pos_y = 1
        pos_x = 1
        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            draw_box(0, 0, width-1, height-1)
            #stdscr.addstr(pos_y, pos_x, "X", curses.A_BOLD)
            # Get user input
            key = stdscr.getch()

            # Exit the loop
            if key == ord('q') or key == ord('Q'):
                break
            elif key == curses.KEY_UP:
                pos_y -= 1
            elif key == curses.KEY_DOWN:
                pos_y += 1
            elif key == curses.KEY_LEFT:
                pos_x -= 1
            elif key == curses.KEY_RIGHT:
                pos_x += 1
                
            if args.debug:
                debug_msg_1 = f"width: {width} height: {height} pos_x: {pos_x} pos_y {pos_y} "
                stdscr.addstr(height-2, 1, debug_msg_1, curses.A_BOLD)
            # Refresh the screen
            stdscr.refresh()
        
        
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
    
    
    # Initial the dht device, with data pin connected to:
    pin_value = getattr(board, "D" + str(pin))
    dhtDevice = device(pin_value, bool(allow_pulseio))
    

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
                    
                    error_msg.append(error.args[0])
                    error_happen = 1
                    now = datetime.now()
                    
                    # Add entry to logs
                    logs.append("Error hapenned at " + now.strftime("%d/%m/%Y, %H:%M:%S"))
                    break
                    # Errors happen fairly often, DHT's are hard to read, just keep going

            if not temperature == None: 
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
                    
                    
                    # Set up the info box
                    box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window1')
                    
                    debug_msg = f"W1: {box_width}x{box_height} " 
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
                    stdscr.addstr(lower_y, lower_x, "Temperature: " + str(temperature) + " C") # w.i.p. make it for Far. as well
                    lower_y += 1
                    stdscr.addstr(lower_y, lower_x, "Humidity: " + str(humidity) + "%" )
                    lower_y += 1
                    stdscr.addstr(lower_y, lower_x, "Sensor delay: " + f"{time_took:.3f} Seconds")
                    
                    # Add additional information about Excel and image
                    msg_2 = None      
                    for msg in info_xl:
                        xl_info_amount += 1
                        # Check if the error message is bigger than the width of the box and add \n to conpensate
                        if len(msg) > box_width-3:
                            msg_2 = msg[box_width-3:]
                            msg = msg[:box_width-3] 
                        stdscr.addstr(lower_y+xl_info_amount , lower_x, msg)
                        if not msg_2 == None:
                            xl_info_amount += 1 
                            stdscr.addstr(lower_y+xl_info_amount , lower_x, msg_2) 
                               
                    
                    # Turn on color pair
                    stdscr.attron(curses.color_pair(3))

                    # Draw graph

                    # Set up the graph box

                    box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window2')

                    debug_msg = debug_msg + f"W2: {box_width}x{box_height} " 
                    
                    # Set up the graph
                    graph_x = box_x + 1
                    graph_x_axis = box_height // 2 + box_y

                    # Draw box and title
                    graph_name = "Temperature"
                    
                    
                    # Calculate the x-coordinate to center the text
                    text_x = box_x + box_width // 2 - len(graph_name) // 2 
                    
                    stdscr.addstr(box_y-1, text_x, graph_name, curses.A_BOLD)
                    
                    # Calculate the scaling factors
                    if device == dht_convert("DHT11"):
                        max_value = 50
                        min_value = 0 # different for each sensor, this one if for DHT11
                    elif device == dht_convert("DHT22"):
                        max_value = 80
                        min_value = 0 # -40 breaks graph
                    else:
                        max_value = 80
                        min_value = 0
                    scale_factor = (max_value-min_value)/(box_height-2)
                
                    
                    # Generate scaled values for demonstration
                    scaled_values = [int(scale_factor * value) for value in range(box_height - 2, -1, -1)]
                    
                    for y, value in enumerate(scaled_values):
                        stdscr.addstr(y + box_y + 1 , box_x + box_width + 1, str(value),curses.A_BOLD)
                    
                    # Draw the graph points 
                    
                    debug_str = ""
                    # Check if list is too big
                    
                    if len(temperature_hold) >= box_width-2:
                        save_and_reset_array(temperature_hold)
                    
                    # Draw graph line
                    for k, value in enumerate(temperature_hold):
                        x = 1 + k
                        for d, value_y in enumerate(scaled_values[::-1]):

                            if value >= value_y:
                                y = d
                        
                        box_y_start = box_y + box_height
                        
                        stdscr.addch(box_y_start-1-y, box_x + x, "•", curses.A_BOLD)

                    
                    # Set up error messages

                    box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window4')
                    
                    debug_msg = debug_msg + f"W4: {box_width}x{box_height} " 
                    
                    stdscr.attroff(curses.color_pair(2))
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
                                            
                    # Set up logs.
                    
                    box_x,box_y,box_width, box_height = window_info.get_window_coordinates('window3')
                    
                    debug_msg = debug_msg + f"W3: {box_width}x{box_height} " 
                    
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
                        
                    cli_bottom_bar(debug_msg)                            
                        
                    
                    
                    
                    
                    # Get user input
                    key = stdscr.getch()

                    # Exit the loop
                    if key == ord('q') or key == ord('Q'):
                        return 0
                    elif key == ord('s') or key == ord('S'): # w.i.p.
                        cli_settings_menu()
                    elif key == ord('c') or key == ord('C'):
                        pass
                
                    i -= 1
                    errors_amount = 0
                    xl_info_amount = 0
                    logs_amount = 0
                    
                    # Refresh the screen
                    stdscr.refresh()
            
            error_happen = 0
            
            if not temperature == None:
                if allowtxt == 1:
                    write_to_txt(temperature,humidity)
                if allowxl == 1 or allowimg == 1:
                # flag == 1 -> allow only xl, flag == 2 allow only image, flag == 3 allow both
                    flag = 0
                    if allowxl == 1 and allowimg == 1:
                        flag = 3
                    elif allowxl == 1 and allowimg == 0:
                        flag = 1
                    else:
                        flag = 2
                    info_xl = write_to_xl(temperature,humidity,flag)
            
        except Exception as error:
                dhtDevice.exit()
                raise error
        except KeyboardInterrupt:
                print("Quitting the program!")
                raise SystemExit
    
curses.wrapper(main)
