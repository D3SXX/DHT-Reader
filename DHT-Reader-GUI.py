#DHT Reader v0.30 alpha by D3SXX

try:
    import os
    import time
    from datetime import datetime
    import configparser
    import board
    import adafruit_dht
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure  # Import Figure from matplotlib.figure
    import xlsxwriter
    import argparse
    import shutil
    import curses
    import tkinter as tk
    import tkinter.ttk as ttk
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


# Array for holding temperature and humidity
temperature_hold = []
humidity_hold = []

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

parser = argparse.ArgumentParser(description='A DHT-Reader CLI Interface')
parser.add_argument('--skip', action='store_true', help='Skip config check')
parser.add_argument('--debug', action='store_true', help='Show debug info')
    
args = parser.parse_args()

if not args.skip:
    flag = 2
    select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename = read_and_write_config(flag, select_theme, temperature_unit, device,pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename,excel_filename, img_filename)




# Initial the dht device, with data pin connected to:
pin_value = getattr(board, "D" + str(pin))
dhtDevice = device(pin_value, bool(allow_pulseio))

old_delay_sec = delay_sec

def update_temperature_humidity():
    global delay_sec
    global old_delay_sec
    try:
        if delay_sec == old_delay_sec:
            humidity, temperature = None, None
            start_time = time.time()
            while humidity is None or temperature is None:
                try:
                    temperature = dhtDevice.temperature
                    humidity = dhtDevice.humidity
                except RuntimeError as error:
                    # Handle errors and log them
                    #error_msg.append(error.args[0])
                    #error_happen = 1
                    now = datetime.now()
                    #logs.append("Error happened at " + now.strftime("%d/%m/%Y, %H:%M:%S"))
                    break

            # Update tk values
            tk_temperature.set(temperature)
            tk_humidity.set(humidity)

            if temperature is not None:
                if temperature_unit == "F":
                    temperature = int(1.8 * temperature + 32)
                temperature_hold.append(temperature)
                humidity_hold.append(humidity)
                update_graph()
            end_time = time.time()
            time_took = end_time - start_time

        # Update the countdown variable
        tk_countdown.set(f"{delay_sec} seconds")
        delay_sec -= 1  # Decrement the delay

        # Schedule the next update
        if delay_sec >= 0:
            window.after(1000, update_temperature_humidity)  # Schedule the next update after 1 second
        else:
            tk_countdown.set(f"0 seconds")  # Set countdown to 0 when the delay is complete
            delay_sec = old_delay_sec
            window.after(1000, update_temperature_humidity)
    
    except Exception as error:
        dhtDevice.exit()
        raise SystemExit(error)
    except KeyboardInterrupt:
        raise SystemExit

def update_graph():
    a.clear()
    a.plot(temperature_hold, label='Temperature')
    a.plot(humidity_hold, label='Humidity')
    a.set_xlabel('Time')
    a.set_ylabel('Value')
    a.legend()
    canvas.draw()



    
# Default filenames
txt_filename = "T_and_H.txt"
excel_filename = "T_and_H.xlsx"
img_filename = "T_and_H.png"




window = tk.Tk()
window.title("DHT Reader v0.3")

window.columnconfigure(0, minsize=200)
window.columnconfigure([0, 1, 2, 3], minsize=50)

frame_info = tk.Frame(master=window)
frame_graph = tk.Frame(master=window)
frame_logs = tk.Frame(master=window)
frame_errors = tk.Frame(master=window)

# Variables to store values in information box
tk_temperature = tk.StringVar(window,"None")
tk_humidity = tk.StringVar(window,"None")
tk_countdown = tk.StringVar()
tk_countdown.set(f"{delay_sec} seconds")

# Information box
temperature_string_label = tk.Label(window, text="Temperature:")
temperature_string_label.grid(row=0, column=0)

temperature_label = tk.Label(window, textvariable=tk_temperature)
temperature_label.grid(row=0, column=1)

humidity_string_label = tk.Label(window, text="Humidity:")
humidity_string_label.grid(row=1, column=0)

humidity_label = tk.Label(window, textvariable=tk_humidity)
humidity_label.grid(row=1, column=1)

countdown_string_label = tk.Label(window, text="The next update:")
countdown_string_label.grid(row=2, column=0)

countdown_label = tk.Label(window, textvariable=tk_countdown)
countdown_label.grid(row=2, column=1)

# Graph box

frame_graph = tk.Frame(master=window)
frame_graph.grid(row=0, column=2, rowspan=3, padx=10, pady=10)

# Create the figure and axis for the interactive graph
fig = Figure(figsize=(5, 5), dpi=100)
a = fig.add_subplot(111)
a.set_xlabel('Time')
a.set_ylabel('Value')
a.legend()

# Embed the figure in the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=frame_graph)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Add the navigation toolbar for basic interaction
toolbar = NavigationToolbar2Tk(canvas, frame_graph)
toolbar.update()




update_graph()
window.after(1000, update_temperature_humidity)       
        


    
window.mainloop()
