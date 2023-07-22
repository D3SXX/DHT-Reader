#DHT Reader v0.3 alpha 2 by D3SXX

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
    import tkinter as tk
    import tkinter.ttk as ttk
except:
    raise SystemExit("Some dependencies are missing. Please run the following command to install them:\npip3 install adafruit_blinka adafruit-circuitpython-dht matplotlib xlsxwriter")

version = "v0.3 alpha 2"

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

logs = ""
errors = ""

# Default values
allowtxt = 0
allowxl = 0
allowimg = 0
delay_sec = 5
allow_pulseio = 1
reset_data = 0
device = "DHT11"
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
    select_theme, temperature_unit, device, pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename = read_and_write_config(flag, select_theme, temperature_unit, device, pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename)

# Initial the dht device, with data pin connected to:
pin_value = getattr(board, "D" + str(pin))
dhtDevice = device(pin_value, bool(allow_pulseio))

old_delay_sec = delay_sec

def on_settings():
    global settings_window
    global frame_right
    global tk_settings_desc_2 
    global device_1_button 
    
    def on_selection_changed(event):
        global device
        selected_item = option_var.get()
        device = dht_convert(selected_item)
        tk_device.set(f"Device: {selected_item}")
        print(f"Selected item: {selected_item} device name: {dht_convert(device)}")
    
    def on_pin_entry_return(event):
        global pin
        pin = pin_entry_var.get()
        tk_pin.set(f"Pin: {pin}")
        print(f"Entered item: {pin_entry_var.get()} new pin: {pin}")
    
    def on_select(event):
        
        global device
        global tk_device
        global tk_pin
        
        selected_index = listbox.curselection()
        
        for widget in frame_right.winfo_children():
            widget.pack_forget()
            
        if selected_index:
            if selected_index[0] == 0:
                global option_var
                global pin_entry_var
                
                tk_settings_info.set("Device and pin settings\n")
                tk_settings_desc.set(f"DHT devices that are supported by the program are:")
                tk_settings_desc_list.set("DHT11, DHT21, DHT22\n")
                tk_settings_desc_2.set(f"Pins allow to read the dht device, in theory any pin should work")
                
                settings_information_label = tk.Label(frame_right, textvariable=tk_settings_info, anchor="n", bg="white")
                settings_information_label.pack(fill="x")
                
                settings_description_label = tk.Label(frame_right, textvariable=tk_settings_desc, anchor="nw", bg="white", wraplength=400)
                settings_description_label.pack(fill="x")
                
                settings_description_list_label = tk.Label(frame_right, textvariable=tk_settings_desc_list, anchor="n", bg="white")
                settings_description_list_label.pack(fill="x")
                
                # Create a new frame to hold the OptionMenu widget
                option_frame = tk.Frame(frame_right, bg="white")
                option_frame.pack(fill="x")
                
                device_options = ["DHT11", "DHT21", "DHT22"]
                option_var = tk.StringVar(option_frame)
                print(f"Menu options: {device_options} current device: {dht_convert(device)}")
                
                if dht_convert(device) == "DHT11": # Set the default option (depends on the current device)
                    option_var.set(device_options[0])
                elif dht_convert(device) == "DHT21":
                    option_var.set(device_options[1])  
                elif dht_convert(device) == "DHT22":
                    option_var.set(device_options[2])  
                
                device_label_var = tk.StringVar(option_frame, f"Current device: ")
                device_label = tk.Label(option_frame, textvariable=device_label_var, bg="white")
                device_label.pack(side="left")
                      
                option_menu = tk.OptionMenu(option_frame, option_var, *device_options, command=on_selection_changed)
                option_menu.pack(fill="x")
                
                settings_nl_label = tk.Label(frame_right, textvariable=tk_settings_nl, anchor="n", bg="white")
                settings_nl_label.pack(fill="x")
                
                settings_description_2_label = tk.Label(frame_right, textvariable=tk_settings_desc_2, anchor="nw", bg="white", wraplength=400)
                settings_description_2_label.pack(fill="x")
                
                # Create a new frame to hold the Entry widget
                entry_frame = tk.Frame(frame_right, bg="white")
                entry_frame.pack(fill="x")
                
                print(f"Current pin: {pin}")
                pin_label_var = tk.StringVar(entry_frame, f"Current pin: ")
                pin_label = tk.Label(entry_frame, textvariable=pin_label_var, bg="white")
                pin_label.pack(side="left")
                
                # Pin Entry
                pin_entry_var = tk.StringVar(entry_frame)
                pin_entry_var.set(pin)  # Set the default value to the current variable
                pin_entry = tk.Entry(entry_frame, textvariable=pin_entry_var)
                pin_entry.pack()
                
                # Bind the "Return" key event to the Entry widget
                pin_entry.bind("<Return>", on_pin_entry_return)        
                
            elif selected_index[0] == 1:
                tk_settings_info.set("Save & Reset data")
                tk_settings_desc.set("You can select which data you want to save and in which formats")
                
                settings_information_label = tk.Label(frame_right, textvariable=tk_settings_info, anchor="n", bg="white")
                settings_information_label.pack(fill="x")

                settings_description_label = tk.Label(frame_right, textvariable=tk_settings_desc, anchor="nw", bg="white", wraplength=400)
                settings_description_label.pack(fill="x")
                
                
            elif selected_index[0] == 2:
                tk_settings_info.set("Extra")
                
                
            selected_item = listbox.get(selected_index)
            if args.debug:
                print(f"Selected item: {selected_item} {selected_index[0]}")

    # Create a new instance of Tk for the new window
    settings_window = tk.Tk()
    settings_window.title("Settings")


    # Set the minimum size for the window (width, height)
    settings_window.minsize(600, 300)
    settings_window.maxsize(800, 600)

    settings_width = settings_window.winfo_width()
    settings_height = settings_window.winfo_height()

    tk_settings_nl = tk.StringVar(settings_window, "\n")
    tk_settings_info = tk.StringVar(settings_window)
    tk_settings_desc = tk.StringVar(settings_window)
    tk_settings_desc_list = tk.StringVar(settings_window)
    tk_settings_desc_2 = tk.StringVar(settings_window)

    # Define the layout using the grid geometry manager
    settings_window.grid_rowconfigure(0, weight=3)
    settings_window.grid_columnconfigure(0, weight=3, minsize=100)  # 30% width
    settings_window.grid_columnconfigure(1, weight=7)  # 70% width
    
    # Create four subframes for the grids
    frame_left = tk.Frame(master=settings_window, bg="white")
    frame_right = tk.Frame(master=settings_window, bg="white")

    # Grid layout for the four subframes
    frame_left.grid(row=0, column=0, sticky="nsew")
    frame_right.grid(row=0, column=1,sticky="nsew", padx = 2, pady = 10)

    # Listbox container
    listbox_container = tk.Frame(master=frame_left)
    listbox_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Create a Listbox with some options
    options = [f"Device & Pin", f"Data Save & Reset", "Extra"]
    listbox = tk.Listbox(listbox_container, selectmode=tk.SINGLE)
    for option in options:
        listbox.insert(tk.END, option)

    # Bind the selection event to the on_select function
    listbox.bind("<<ListboxSelect>>", on_select)

    # Pack the Listbox to display it
    listbox.pack(padx=5, pady=10, fill=tk.BOTH, expand=True)
    
    # Start the event loop for the new window
    settings_window.mainloop()

def on_close():
    dhtDevice.exit()
    print("DHT device disabled, closing the program")
    window.destroy()
    try:
        settings_window.destroy()
    except:
        pass

def update_temperature_humidity():
    global delay_sec
    global old_delay_sec
    global logs
    global errors
    global graph_width
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
                    errors += error.args[0] + "\n"
                    now = datetime.now()
                    logs += ("Error happened at " + now.strftime("%d/%m/%Y, %H:%M:%S") + "\n")
                    tk_logs.set(logs)
                    tk_errors.set(errors)
                    break

            # Update tk values
            tk_temperature.set(f"Temperature: {temperature}")
            tk_humidity.set(f"Humidity: {humidity}")

            if temperature is not None:
                if temperature_unit == "F":
                    temperature = int(1.8 * temperature + 32)
                temperature_hold.append(temperature)
                humidity_hold.append(humidity)
                update_graph()
            end_time = time.time()
            time_took = end_time - start_time

        # Update the countdown variable
        tk_countdown.set(f"The next update: {delay_sec} seconds")
        delay_sec -= 1  # Decrement the delay

        # Schedule the next update
        if delay_sec >= 0:
            window.after(1000, update_temperature_humidity)  # Schedule the next update after 1 second
        else:
            tk_countdown.set(f"The next update: 0 seconds")  # Set countdown to 0 when the delay is complete
            delay_sec = old_delay_sec
            window.after(1000, update_temperature_humidity)
        if args.debug:
            tk_debug.set(f"Debug {window.winfo_width()}x{window.winfo_height()}")
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
    
window = tk.Tk()
window.title("DHT Reader " + version)

# Set the minimum size for the window (width, height)
window.minsize(800, 600)

# Define the layout using the grid geometry manager
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

# Create four subframes for the grids
frame_top_left = tk.Frame(master=window, bg="white")
frame_top_right = tk.Frame(master=window, bg="white")
frame_bottom_left = tk.Frame(master=window, bg="white")
frame_bottom_right = tk.Frame(master=window, bg="white")

# Grid layout for the four subframes
frame_top_left.grid(row=0, column=0, sticky="nsew")
frame_top_right.grid(row=0, column=1, sticky="nsew")
frame_bottom_left.grid(row=1, column=0, sticky="nsew")
frame_bottom_right.grid(row=1, column=1, sticky="nsew")

# Variables to store values in information box

tk_device = tk.StringVar(window, f"Device: {dht_convert(device)}")
tk_pin = tk.StringVar(window, f"Pin: {pin}")
tk_temperature = tk.StringVar(window, "Temperature: ")
tk_humidity = tk.StringVar(window, "Humidity: ")
tk_countdown = tk.StringVar()
tk_countdown.set(f"{delay_sec} seconds")
tk_logs = tk.StringVar(window)
tk_errors = tk.StringVar(window)

# Graph box
frame_graph = tk.Frame(master=window)
frame_graph.grid(row=0, column=1, rowspan=3, padx=1, pady=1)

# Create the GUI elements and layout for each subframe
# Subframe: Top Right (Graph)
# Create the figure and axis for the interactive graph

graph_label = tk.Label(frame_top_right, text="Graph")
graph_label.pack(fill="x", padx=1)

fig = Figure(figsize=(5,4), dpi=100)
a = fig.add_subplot(111)
a.set_xlabel('Time')
a.set_ylabel('Value')
a.legend()

# Embed the figure in the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=frame_top_right)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Add the navigation toolbar for basic interaction
toolbar = NavigationToolbar2Tk(canvas, frame_top_right)
toolbar.update()
toolbar.mode = "None"
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Subframe: Top Left (Information)
# Labels and Entry widgets

information_label = tk.Label(frame_top_left, text="Information")
information_label.pack(fill="x", padx=1)

device_label = tk.Label(frame_top_left, textvariable=tk_device, anchor="nw", bg="white")
device_label.pack(fill="x")

pin_label = tk.Label(frame_top_left, textvariable=tk_pin, anchor="nw", bg="white")
pin_label.pack(fill="x")

temperature_label = tk.Label(frame_top_left, textvariable=tk_temperature, anchor="nw", bg="white")
temperature_label.pack(fill="x")

humidity_label = tk.Label(frame_top_left, textvariable=tk_humidity, anchor="nw", bg="white")
humidity_label.pack(fill="x")

countdown_label = tk.Label(frame_top_left, textvariable=tk_countdown, anchor="nw", bg="white")
countdown_label.pack(fill="x")

settings_button = tk.Button(frame_top_left, text ="Settings", command = on_settings, anchor="sw")
settings_button.pack(side="bottom",fill="x")


if args.debug:
    tk_debug = tk.StringVar(window)
    debug_label = tk.Label(frame_top_left, textvariable=tk_debug, anchor="sw", bg="white")
    debug_label.pack(side="bottom",fill="x")


# Subframe: Bottom Left (Logs)
# Labels and Entry widgets
logs_label = tk.Label(frame_bottom_left, text="Logs")
logs_label.pack(fill="x")

logs_logs_label = tk.Label(
    frame_bottom_left,
    textvariable=tk_logs,
    bg="black",
    fg="white",
    height=10,
    anchor="nw",
)
logs_logs_label.pack(fill="x")

# Subframe: Bottom Right (Errors)
# Labels and Entry widgets
errors_label = tk.Label(frame_bottom_right, text="Errors")
errors_label.pack(fill="x",padx=1)

errors_errors_label = tk.Label(
    frame_bottom_right,
    textvariable=tk_errors,
    bg="black",
    fg="red",
    height=10,
    anchor="nw",
)
errors_errors_label.pack(fill="x", padx=1)

window.protocol("WM_DELETE_WINDOW", on_close)


update_graph()
window.after(1000, update_temperature_humidity)

window.mainloop()
