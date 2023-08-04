#DHT Reader v0.3 hotfix 2 by D3SXX

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
    from matplotlib.figure import Figure
    import xlsxwriter
    import argparse
    import shutil
    import tkinter as tk
    import tkinter.ttk as ttk
except:
    raise SystemExit("Some dependencies are missing. Please run the following command to install them:\npip3 install adafruit_blinka adafruit-circuitpython-dht matplotlib xlsxwriter")

version = "v0.3"
        
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
                    return select_theme, temperature_unit, dht_convert(device),pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename  
            except:
                print(f"Config file {config_file} doesn't exist, using default values")
                return select_theme, temperature_unit, dht_convert(device),pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename  
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
        print(f"An image {img_filename} ({img_size} bytes) was created in {full_time:.2f} seconds")
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
    print(f"An Excel file {excel_filename} ({xl_size} bytes) with {a} entries was created")
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
    print(f"{txt_filename} ({txt_size} bytes) file was updated ")
    return [str(f"{txt_filename} ({txt_size} bytes) file was updated ")]

def init_device(flag, device, pin, allow_pulseio):
    global dhtDevice
    if flag != 1:
        dhtDevice.exit()
    # Initial the dht device, with data pin connected to:
    pin_value = getattr(board, "D" + str(pin))
    dhtDevice = device(pin_value, bool(allow_pulseio))
    if flag != 3:
        print(f"Device {dht_convert(device)} with pin {pin} initialized\nPulseio is set to {bool(allow_pulseio)}")

def insert_log_error(flag, log_msg = "", error_msg = ""):
    # flag == 1 --> add log only, flag == 2 --> add error only, flag == 3 --> both
    if flag == 1:
        logs_listbox.insert(tk.END, log_msg)
        logs_listbox.see(tk.END)
        if args.debug:
            print(log_msg)
    elif flag == 2:
        errors_listbox.insert(tk.END, error_msg)
        errors_listbox.see(tk.END)
        if args.debug:
            print(error_msg)
    else:
        logs_listbox.insert(tk.END, log_msg)
        logs_listbox.see(tk.END)
        errors_listbox.insert(tk.END, error_msg)
        errors_listbox.see(tk.END)
        if args.debug:
            print(log_msg)
            print(error_msg)

def change_theme(select):
    global background_main, background_errors_logs, background_title,background_button, foreground_main, foreground_logs, foreground_errors
    if select == 0:
        background_main = "white"
        background_errors_logs = "white"
        background_title = "lightgray"
        background_button = "lightgray"
        foreground_main = "black"
        foreground_logs = "black"
        foreground_errors = "red"
    elif select == 1:
        background_main = "black"
        background_errors_logs = "black"
        background_title = "gray"
        background_button = "#3d3d5c"
        foreground_main = "white"
        foreground_logs = "white"
        foreground_errors = "red"
    elif select == 2:
        background_main = "black"
        background_errors_logs = "black"
        background_title = "purple"
        background_button = "#3d3d5c"
        foreground_main = "white"
        foreground_logs = "white"
        foreground_errors = "red"
    elif select == 3:
        background_main = "blue"
        background_errors_logs = "blue"
        background_title = "gray"
        background_button = "#3d3d5c"
        foreground_main = "white"
        foreground_logs = "white"
        foreground_errors = "red"

def auto_detect(flag = 0, scan_all = 1, first_pin = 0, last_pin = 20):
    pin = 0
    allow_pulseio = 1
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
        max_value_pg = (last_pin+1-first_pin)*3*2-cut_val+val
        progress_bar["value"] = first_pin
        progress_bar["maximum"] = max_value_pg
        
    for current_device in devices:
        msg = f"Checking the {current_device}"
        if flag == 1:
            autodetect_listbox.insert(tk.END, msg)
            autodetect_listbox.see(tk.END)
            autodetect_listbox.update_idletasks()
        print(msg)
        device = dht_convert(current_device)
        for allow_pulseio in range(1,-1,-1):
            msg = f"Pulseio is set to {bool(allow_pulseio)}"
            if flag == 1:
                autodetect_listbox.insert(tk.END, msg)
                autodetect_listbox.see(tk.END)
                autodetect_listbox.update_idletasks()
            print(msg)
            for pin in range(first_pin,last_pin+1):
                try:
                    if pin == 7 or pin == 8:
                        continue
                    init_device(3, device, pin, allow_pulseio)
                    msg = f"Checking pin {pin}"
                    if flag == 1:
                        autodetect_listbox.insert(tk.END, msg)
                        autodetect_listbox.see(tk.END)
                        progress_bar["value"] += 1
                        autodetect_listbox.update_idletasks()
                    print(msg)
                    temperature = dhtDevice.temperature
                    humidity = dhtDevice.humidity
                    print(temperature,humidity)
                    msg = f"Detected {current_device} at pin {pin} (Pulseio is set to {bool(allow_pulseio)})"
                    if flag == 1:
                        autodetect_listbox.insert(tk.END, msg)
                        autodetect_listbox.see(tk.END)
                        if scan_all == 0:
                            progress_bar["value"] = max_value_pg
                        autodetect_listbox.update_idletasks()
                    print(msg)
                    tk_device.set(f"Device: {current_device}")
                    tk_pin.set(f"Pin: {pin}")
                    if scan_all == 0:
                        return 0
                except RuntimeError as error:
                    if str(error) == "DHT sensor not found, check wiring":
                        print(f"Error: {error}")
                        
                    else:
                        print(error)
                        msg = f"Detected {current_device} at pin {pin} (Pulseio is set to {bool(allow_pulseio)})"
                        if flag == 1:
                            autodetect_listbox.insert(tk.END, msg)
                            autodetect_listbox.see(tk.END)
                            if scan_all == 0:
                                progress_bar["value"] = max_value_pg
                            autodetect_listbox.update_idletasks()
                        print(msg)
                        tk_device.set(f"Device: {current_device}")
                        tk_pin.set(f"Pin: {pin}")
                        if scan_all == 0:
                            return 0

# Array for holding temperature and humidity
temperature_hold = []
humidity_hold = []
info_xl = []

# Default values
allowtxt = 0
allowxl = 0
allowimg = 0
delay_sec = 5
allow_pulseio = 1
reset_data = 0
device = "DHT11"
pin = 4
select_theme = 0
temperature_unit = "C"
graph_environment = "Temperature"

graph_show = "Both"

# Default filenames
txt_filename = "T_and_H.txt"
excel_filename = "T_and_H.xlsx"
img_filename = "T_and_H.png"

parser = argparse.ArgumentParser(description='A DHT-Reader CLI Interface')
parser.add_argument('--skip', action='store_true', help='Skip config check')
parser.add_argument('--debug', action='store_true', help='Show debug info')
parser.add_argument('--autodetect', action='store_true', help='Auto detect device')
args = parser.parse_args()

if not args.skip:
    flag = 2
    select_theme, temperature_unit, device, pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename = read_and_write_config(flag, select_theme, temperature_unit, device, pin, allowtxt, allowxl, allowimg, delay_sec, allow_pulseio, reset_data, graph_environment, txt_filename, excel_filename, img_filename)
else:
    device = dht_convert(device)
init_device(1, device, pin, allow_pulseio)
change_theme(select_theme)

old_delay_sec = delay_sec

def on_autodetect():
    def change_scan_all():
        global scan_all
        scan_all = not bool(scan_all)
        if args.debug:
            insert_log_error(1, f"scan_all is set to {scan_all}")

    def on_enter_first_pin(event):
        global first_pin
        first_pin = int(first_pin_entry.get())
        if args.debug:
            insert_log_error(1, f"first_pin is set to {first_pin}")

    def on_enter_last_pin(event):
        global last_pin
        last_pin = int(last_pin_entry.get())
        if args.debug:
            insert_log_error(1, f"last_pin is set to {last_pin}")

    global autodetect_listbox, progress_bar, scan_all, first_pin, last_pin

    scan_all = False
    first_pin = 0
    last_pin = 20
    s = ttk.Style()
    s.configure("Custom.TLabelframe", background=background_main)

    def on_close_autodetect():
        autodetect_window.destroy()

    # Create a new instance of Tk for the new window
    autodetect_window = tk.Tk()
    autodetect_window.title("Auto detect")

    # Set the minimum size for the window (width, height)
    autodetect_window.minsize(450, 150)
    autodetect_window.maxsize(600, 200)

    if args.debug:
        insert_log_error(1, "Auto detect window open")

    # Create a new frame to hold the Auto detect widgets
    window_frame = ttk.Frame(master=autodetect_window, style="Custom.TFrame")
    window_frame.pack(fill="both", expand=True)

    autodetect_frame_button = ttk.Button(window_frame, text="Detect Device", command=lambda: auto_detect(1, int(scan_all), first_pin, last_pin), style="Custom.TButton")
    autodetect_frame_button.grid(row=0, column=0)
    
    scan_all_checkbox = tk.Checkbutton(window_frame, text="Don't stop scanning",command=change_scan_all)
    scan_all_checkbox.grid(row=1, column=0)
    
    if scan_all:
        scan_all_checkbox.state(['selected'])

    # Create a LabelFrame to group the label and entries
    pins_frame = ttk.LabelFrame(window_frame, text="First and last pins to scan", padding=5, style="Custom.TLabelframe")
    pins_frame.grid(row=2, column=0, sticky="ew")

    pins_frame_content = ttk.Frame(pins_frame, style="Custom.TFrame", padding=5)  # Separate frame for content with background color
    pins_frame_content.pack(fill="both", expand=True)

    first_pin_label = ttk.Label(pins_frame_content, text="First pin:", style="Custom.TLabel")
    first_pin_label.grid(row=0, column=0)

    first_pin_entry = ttk.Entry(pins_frame_content, style="Custom.TEntry")
    first_pin_entry.grid(row=0, column=1)
    first_pin_entry.insert(0, first_pin)
    first_pin_entry.bind("<Return>", on_enter_first_pin)

    last_pin_label = ttk.Label(pins_frame_content, text="Last pin:", style="Custom.TLabel")
    last_pin_label.grid(row=1, column=0)

    last_pin_entry = ttk.Entry(pins_frame_content, style="Custom.TEntry")
    last_pin_entry.grid(row=1, column=1)
    last_pin_entry.insert(0, last_pin)
    last_pin_entry.bind("<Return>", on_enter_last_pin)

    # Create a Listbox widget
    autodetect_listbox = tk.Listbox(window_frame, selectmode=tk.SINGLE, bg=background_errors_logs, fg=foreground_logs)
    autodetect_listbox.grid(row=0, column=1, rowspan=3, sticky="nsew")

    # Create a Scrollbar widget
    autodetect_scrollbar = ttk.Scrollbar(window_frame, command=autodetect_listbox.yview)
    autodetect_scrollbar.grid(row=0, column=2, rowspan=3, sticky="ns")

    # Configure the Listbox to use the Scrollbar
    autodetect_listbox.config(yscrollcommand=autodetect_scrollbar.set)

    # Create a Progressbar widget
    progress_bar = ttk.Progressbar(window_frame, orient="horizontal", mode="determinate")
    progress_bar.grid(row=3, column=0, columnspan=3, sticky="ew", padx=20, pady=5)

    # Make the rows and columns expandable
    window_frame.columnconfigure(1, weight=1)
    window_frame.rowconfigure(3, weight=1)

    autodetect_window.mainloop()

def on_settings():
    global settings_window
    global frame_right
    global tk_settings_desc_2 
    global device_1_button 
    
    def on_selection_changed(event):
        global device
        global pin
        selected_item = option_var.get()
        device = dht_convert(selected_item)
        tk_device.set(f"Device: {selected_item}")
        insert_log_error(1,f"Device was changed to {dht_convert(device)}")
        init_device(0, device, pin, allow_pulseio)
    
    def on_pin_entry_return(event):
        global device
        global pin
        pin = pin_entry_var.get()
        tk_pin.set(f"Pin: {pin}")
        insert_log_error(1,f"Pin was changed to {pin}")
        init_device(0, device, pin, allow_pulseio)
    
    def on_checkbox_change(option):
        if option == 0:
            global allowtxt
            allowtxt = not allowtxt
            insert_log_error(1,f"Writing to a txt file is set to {bool(allowtxt)}")

        elif option == 1:
            global allowxl
            allowxl = not allowxl
            insert_log_error(1,f"Writing to a Excel file is set to {bool(allowxl)}")
        elif option == 2:
            global allowimg
            allowimg = not allowimg
            insert_log_error(1,f"Writing to an Image file is set to {bool(allowimg)}")
        elif option == 3:
            global allow_pulseio
            allow_pulseio = not allow_pulseio
            insert_log_error(1,f"Using Pulseio is set to {bool(allow_pulseio)}")
            init_device(0, device, pin, allow_pulseio) 
        elif option == 4:
            global reset_data
            reset_data = not reset_data
            insert_log_error(1,f"Reset data at startup is set to {bool(reset_data)}")
            
    def on_filename_entry_return(option, value):
        if option == 0:
            global txt_filename
            txt_filename = value.get()
            print(f"New txt filename: {txt_filename}")
            insert_log_error(1,f"Text filename was changed to {txt_filename}")
        elif option == 1:
            global excel_filename
            excel_filename = value.get()
            print(f"New Excel filename: {excel_filename}")
            insert_log_error(1,f"Excel filename was changed to {excel_filename}")
        elif option == 2:
            global img_filename
            img_filename = value.get()
            print(f"New image filename: {img_filename}")
            insert_log_error(1,f"Image filename was changed to {img_filename}")
    
    def change_temperature_unit(unit):
        global temperature_unit
        if unit == "C":
            c_unit_button.config(relief=tk.SUNKEN)
            f_unit_button.config(relief=tk.RAISED)
        elif unit == "F":
            c_unit_button.config(relief=tk.RAISED)
            f_unit_button.config(relief=tk.SUNKEN)
        temperature_unit = unit
        insert_log_error(1,f"Temperature unit was changed to °{unit}")
            
    def change_graph(option):
        global graph_show 
        if option == "T":
            graph_show = "Temperature"
            T_graph_change_button.config(relief=tk.SUNKEN)
            T_H_graph_change_button.config(relief=tk.RAISED)
            H_graph_change_button.config(relief=tk.RAISED)
            insert_log_error(1,f"Graph now shows only {graph_show}")
        elif option == "H":
            graph_show = "Humidity"
            T_graph_change_button.config(relief=tk.RAISED)
            T_H_graph_change_button.config(relief=tk.RAISED)
            H_graph_change_button.config(relief=tk.SUNKEN)
            insert_log_error(1,f"Graph now shows only {graph_show}")
        else:
            graph_show = "Both"
            T_graph_change_button.config(relief=tk.RAISED)
            T_H_graph_change_button.config(relief=tk.SUNKEN)
            H_graph_change_button.config(relief=tk.RAISED)
            insert_log_error(1,f"Graph now shows both temperature and humidity")

    def on_change_delay(value, flag = 0):
        global old_delay_sec
        if flag == 1:
            value = value.get()
        if value > 0:
            old_delay_sec = value
            delay_entry_var.set(old_delay_sec)
            delay_decrease_button.config(relief=tk.RAISED)
            insert_log_error(1,f"Delay was changes to {old_delay_sec} second(s)")
            if value == 1:
                delay_decrease_button.config(relief=tk.SUNKEN)
        else:
            delay_decrease_button.config(relief=tk.SUNKEN)
            if args.debug:
                insert_log_error(1,f"debug: delay value is too small to decrease --> {old_delay_sec}")

    def on_theme_select(select):
        global select_theme
        themes_options = ["Default (white)", "Default (black)", "Classic (black)", "Classic (Blue)"]
        select_theme  = themes_options.index(select)
        insert_log_error(1,f"Theme selected: {select}")
        
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
                global checkbox_allowpulseio_var
                
                main_frame = ttk.LabelFrame(frame_right, text="Device and pin settings", padding=5)
                main_frame.pack(anchor="nw", fill="both")
                
                # Create a new frame to hold the OptionMenu widget
                change_device_frame = ttk.LabelFrame(main_frame, text="Change device", padding=5)
                change_device_frame.pack(anchor="nw")
                
                device_options = ["DHT11", "DHT21", "DHT22"]
                option_var = tk.StringVar(change_device_frame)
                if args.debug:
                    insert_log_error(1,f"Select {selected_index[0]} (Device and pin settings)")
                    insert_log_error(1,f"Menu options: {device_options} current device: {dht_convert(device)}")
                    insert_log_error(1,f"Current pin: {pin}")
                    insert_log_error(1,f"pulseio: {bool(allow_pulseio)}")
                if dht_convert(device) == "DHT11": # Set the default option (depends on the current device)
                    option_var.set(device_options[0])
                elif dht_convert(device) == "DHT21":
                    option_var.set(device_options[1])  
                elif dht_convert(device) == "DHT22":
                    option_var.set(device_options[2])  
                
                device_label = ttk.Label(change_device_frame, text="Current device: ")
                device_label.pack(side="left")
                      
                option_menu = tk.OptionMenu(change_device_frame, option_var, *device_options, command=on_selection_changed)
                option_menu.pack(side="left", anchor="w")
                
                # Create a new frame to hold the Entry widget
                entry_frame = ttk.LabelFrame(main_frame, text="Change pin", padding=5)
                entry_frame.pack(anchor="nw")
                
                pin_label = ttk.Label(entry_frame, text="Current pin")
                pin_label.pack(side="left")
                
                # Pin Entry
                pin_entry_var = tk.StringVar(entry_frame)
                pin_entry_var.set(pin)  # Set the default value to the current variable
                pin_entry = tk.Entry(entry_frame, textvariable=pin_entry_var,bg=background_main, fg=foreground_main)
                pin_entry.pack(anchor="w")
                
                # Bind the "Return" key event to the Entry widget
                pin_entry.bind("<Return>", on_pin_entry_return)        
                
                # Optional
                
                # Create a new frame to hold the optional widgets
                optional_frame = ttk.LabelFrame(main_frame, text="Optional", padding=5)
                optional_frame.pack(anchor="nw")
                
                checkbox_allowpulseio_var = tk.BooleanVar(value=bool(allow_pulseio))
                
                allowpulseio_checkbox = tk.Checkbutton(optional_frame, text="Enable Pulseio", variable=checkbox_allowpulseio_var, command=lambda: on_checkbox_change(3))
                allowpulseio_checkbox.pack(anchor="nw")
                if allow_pulseio:
                    allowpulseio_checkbox.select()
                # Create a new frame to hold the Auto detect widgets
                autodetect_frame = ttk.LabelFrame(main_frame, text="Auto detect device", padding=5)
                autodetect_frame.pack(fill="x")
                
                autodetect_frame_button = tk.Button(autodetect_frame, text ="Detect Device", command = on_autodetect)
                autodetect_frame_button.pack(side="left")
                
            elif selected_index[0] == 1:
                
                data_frame = ttk.LabelFrame(frame_right, text="Save and Reset data settings", padding=5)
                data_frame.pack(anchor="nw",fill="both")

                if args.debug:
                    insert_log_error(1,f"Select {selected_index[0]} (Save and Reset data settings)")
                    insert_log_error(1,f"allowtxt: {bool(allowtxt)}")
                    insert_log_error(1,f"allowxl: {bool(allowxl)}")
                    insert_log_error(1,f"allowimg: {bool(allowimg)}")
                    insert_log_error(1,f"txt_filename: {txt_filename}")
                    insert_log_error(1,f"excel_filename: {excel_filename}")
                    insert_log_error(1,f"img_filename: {img_filename}")
                    insert_log_error(1,f"reset_data: {reset_data}")
                    
                # Create a new frame to hold the checkbutton widgets
                checkbutton_frame = ttk.LabelFrame(data_frame, text="Save data to formats:", padding=5)
                checkbutton_frame.pack(anchor="nw")

                allowtxt_checkbox = tk.Checkbutton(checkbutton_frame, text="txt file",command=lambda: on_checkbox_change(0))
                allowtxt_checkbox.pack(anchor="w")
                if allowtxt:
                    allowtxt_checkbox.select()
                
                allowxl_checkbox = tk.Checkbutton(checkbutton_frame, text="Excel file",command=lambda: on_checkbox_change(1))
                allowxl_checkbox.pack(anchor="w")
                if allowxl:
                    allowxl_checkbox.select()
                
                allowimg_checkbox = tk.Checkbutton(checkbutton_frame, text="Image file",command=lambda: on_checkbox_change(2))
                allowimg_checkbox.pack(anchor="w")
                if allowimg:
                    allowimg_checkbox.select()
                
                # Create a new frame to hold the Entry widgets
                entry_frame = ttk.LabelFrame(data_frame, text="Change filenames", padding=5)
                entry_frame.pack(anchor="nw")          
                
                # Change filename for txt
                txt_filename_label = ttk.Label(entry_frame, text="Current txt filename: ")
                txt_filename_label.pack(anchor="w")
                
                # txt Entry
                txt_filename_entry_var = tk.StringVar(entry_frame)
                txt_filename_entry_var.set(txt_filename)  # Set the default value to the current variable
                txt_filename_entry = tk.Entry(entry_frame, textvariable=txt_filename_entry_var, bg=background_main, fg=foreground_main)
                txt_filename_entry.pack(anchor="w")
                
                # Bind the "Return" key event to the Entry widget
                txt_filename_entry.bind("<Return>", lambda event: on_filename_entry_return(0, txt_filename_entry_var))   
                
                # Change filename for Excel
                excel_filename_label = tk.Label(entry_frame, text="Current Excel filename: ")
                excel_filename_label.pack(anchor="w")
                
                # excel Entry
                excel_filename_entry_var = tk.StringVar(entry_frame)
                excel_filename_entry_var.set(excel_filename)  # Set the default value to the current variable
                excel_filename_entry = tk.Entry(entry_frame, textvariable=excel_filename_entry_var, bg=background_main, fg=foreground_main)
                excel_filename_entry.pack(anchor="w")
                
                # Bind the "Return" key event to the Entry widget
                excel_filename_entry.bind("<Return>", lambda event: on_filename_entry_return(1, excel_filename_entry_var))
                
                # Change filename for Image
                img_filename_label = ttk.Label(entry_frame, text="Current Image filename: ")
                img_filename_label.pack(anchor="w")
                
                # excel Entry
                img_filename_entry_var = tk.StringVar(entry_frame)
                img_filename_entry_var.set(img_filename)  # Set the default value to the current variable
                img_filename_entry = tk.Entry(entry_frame, textvariable=img_filename_entry_var, bg=background_main, fg=foreground_main)
                img_filename_entry.pack(anchor="w")
                
                # Bind the "Return" key event to the Entry widget
                img_filename_entry.bind("<Return>", lambda event: on_filename_entry_return(2, img_filename_entry_var))    
                
                # Create a new frame to hold the optional widgets
                optional_frame = ttk.LabelFrame(data_frame, text="Optional", padding=5)
                optional_frame.pack(anchor="nw")
                
                reset_data_var = tk.BooleanVar()
                
                reset_data_checkbox = tk.Checkbutton(optional_frame,variable=reset_data_var, text="Reset data at startup",command=lambda: on_checkbox_change(4))
                reset_data_checkbox.pack(anchor="w")
                if reset_data:
                    reset_data_checkbox.select()
                
            elif selected_index[0] == 2:
                global c_unit_button
                global f_unit_button
                global T_graph_change_button
                global T_H_graph_change_button
                global H_graph_change_button
                global delay_entry_var
                global delay_decrease_button
                global select_theme
                
                general_frame = ttk.LabelFrame(frame_right, text="General settings", padding=5)
                general_frame.pack(anchor="nw",fill="both")
                
                if args.debug:
                    insert_log_error(1,f"Select {selected_index[0]} (General)")
                    insert_log_error(1,f"temperature_unit: {temperature_unit}")
                    insert_log_error(1,f"graph_show: {graph_show}")
                    insert_log_error(1,f"old_delay_sec: {old_delay_sec}")
                    insert_log_error(1,f"select_theme: {select_theme}")
                
                # Change temperature unit
                temperature_unit_frame = ttk.LabelFrame(general_frame, text="Change temperature unit", padding=5)
                temperature_unit_frame.pack(anchor="nw")
                # Create a new frame to hold the temperature unit change widgets
                
                temperature_unit_label = ttk.Label(temperature_unit_frame, text="Unit: ")
                temperature_unit_label.pack(side="left")
                
                c_unit_button = tk.Button(temperature_unit_frame, text ="°C", command = lambda: change_temperature_unit("C"), bg=background_button, fg=foreground_main)
                c_unit_button.pack(side="left")
                f_unit_button = tk.Button(temperature_unit_frame, text ="°F", command = lambda: change_temperature_unit("F"), bg=background_button, fg=foreground_main)
                f_unit_button.pack(side="left")
                
                # Set the initial relief of the buttons based on the current temperature_unit
                c_unit_button.config(relief=tk.SUNKEN if temperature_unit == "C" else tk.RAISED)
                f_unit_button.config(relief=tk.SUNKEN if temperature_unit == "F" else tk.RAISED)
                
                graph_change_frame = ttk.LabelFrame(general_frame, text="Change graph", padding=5)
                graph_change_frame.pack(anchor="nw")
                
                T_graph_change_button = tk.Button(graph_change_frame, text ="Only Temperature", command = lambda: change_graph("T"), bg=background_button, fg=foreground_main)
                T_graph_change_button.pack(side="left")
                T_H_graph_change_button = tk.Button(graph_change_frame, text ="Both", command = lambda: change_graph("Both"), bg=background_button, fg=foreground_main)
                T_H_graph_change_button.pack(side="left")
                H_graph_change_button = tk.Button(graph_change_frame, text ="Only Humidity", command = lambda: change_graph("H"), bg=background_button, fg=foreground_main)
                H_graph_change_button.pack(side="left")
                
                # Set the initial relief of the buttons based on the current graph_show
                T_graph_change_button.config(relief=tk.SUNKEN if graph_show == "Temperature" else tk.RAISED)
                T_H_graph_change_button.config(relief=tk.SUNKEN if graph_show == "Both" else tk.RAISED)
                H_graph_change_button.config(relief=tk.SUNKEN if graph_show == "Humidity" else tk.RAISED)
                
                delay_change_frame = ttk.LabelFrame(general_frame, text="Change delay", padding=5)
                delay_change_frame.pack(anchor="nw")
                
                delay_decrease_button = tk.Button(delay_change_frame, text ="-", command = lambda: on_change_delay(old_delay_sec-1),bg=background_button, fg=foreground_main)
                delay_decrease_button.pack(side="left")
                
                # delay Entry
                delay_entry_var = tk.IntVar(delay_change_frame)
                delay_entry_var.set(old_delay_sec)  # Set the default value to the current variable
                delay_change_entry = tk.Entry(delay_change_frame, textvariable=delay_entry_var,bg=background_main, fg=foreground_main)
                delay_change_entry.pack(side="left")
                
                # Bind the "Return" key event to the Entry widget
                delay_change_entry.bind("<Return>", lambda event: on_change_delay(delay_entry_var,1))   
                
                delay_increase_button = tk.Button(delay_change_frame, text ="+", command = lambda: on_change_delay(old_delay_sec+1),bg=background_button, fg=foreground_main)
                delay_increase_button.pack(side="left")
                
                # Create a new frame to hold the theme change widgets
                theme_change_frame = ttk.LabelFrame(general_frame, text="Change theme", padding=5)
                theme_change_frame.pack(anchor="nw")
                                
                themes_options = ["Default (white)", "Default (black)", "Classic (black)", "Classic (Blue)"]
                option_var = tk.StringVar(theme_change_frame)
                if select_theme == 0: # Set the default option (depends on the select_theme variable)
                    option_var.set(themes_options[0])
                elif select_theme == 1:
                    option_var.set(themes_options[1])  
                elif select_theme == 2:
                    option_var.set(themes_options[2])  
                elif select_theme == 3:
                    option_var.set(themes_options[3]) 
                    
                theme_label = ttk.Label(theme_change_frame, text="Current theme: ")
                theme_label.pack(side="left")
                      
                option_menu = tk.OptionMenu(theme_change_frame,option_var,*themes_options,command=lambda selected_value: on_theme_select(selected_value))

                option_menu.pack(fill="x", anchor="w")
                
                # Set the initial relief of the buttons based on the current graph_show
                delay_decrease_button.config(relief=tk.SUNKEN if old_delay_sec <= 1 else tk.RAISED)
                
            selected_item = listbox.get(selected_index)

    def on_close_settings():
        settings_window.destroy()
        read_and_write_config(1, select_theme, temperature_unit, device,int(pin), int(allowtxt), int(allowxl), int(allowimg), int(old_delay_sec), int(allow_pulseio), int(reset_data), graph_environment, txt_filename, excel_filename, img_filename)
        insert_log_error(1,f"Config file was updated")
        
    # Create a new instance of Tk for the new window
    settings_window = tk.Tk()
    settings_window.title("Settings")


    # Set the minimum size for the window (width, height)
    settings_window.minsize(600, 200)
    settings_window.maxsize(800, 600)
    settings_window.resizable(False, False)
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
    frame_left = tk.Frame(master=settings_window, bg=background_main)
    frame_right = tk.Frame(master=settings_window, bg=background_main)

    # Grid layout for the four subframes
    frame_left.grid(row=0, column=0, sticky="nsew")
    frame_right.grid(row=0, column=1,sticky="nsew", padx = 2, pady = 10)

    # Listbox container
    listbox_container = tk.Frame(master=frame_left)
    listbox_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Create a Listbox with some options
    options = [f"Device & Pin", f"Data Save & Reset", "General"]
    listbox = tk.Listbox(listbox_container, selectmode=tk.SINGLE, bg=background_main, fg=foreground_main)
    for option in options:
        listbox.insert(tk.END, option)

    # Bind the selection event to the on_select function
    listbox.bind("<<ListboxSelect>>", on_select)

    # Pack the Listbox to display it
    listbox.pack(padx=5, pady=10, fill=tk.BOTH, expand=True)
    
    settings_window.protocol("WM_DELETE_WINDOW", on_close_settings)
    
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
    raise SystemExit()

def update_temperature_humidity():
    global delay_sec
    global old_delay_sec
    global logs
    global errors
    global graph_width
    global temperature
    global humidity
    
    delay_progress_bar["maximum"] = old_delay_sec
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
                    now = datetime.now()
                    now = now.strftime("%d/%m/%Y, %H:%M:%S")
                    insert_log_error(3,f"Error happened at {now}",error.args[0])
                    break

            if temperature is not None:
                if temperature_unit == "F":
                    temperature = int(1.8 * temperature + 32)
                temperature_hold.append(temperature)
                humidity_hold.append(humidity)
                update_graph()
            end_time = time.time()
            time_took = end_time - start_time

        # Update tk values
        tk_temperature.set(f"Temperature: {temperature} °{temperature_unit}")
        tk_humidity.set(f"Humidity: {humidity} %")
        
        if delay_sec != old_delay_sec:
            delay_progress_bar["value"] += 1
        else:
            delay_progress_bar["value"] = 0
        # Update the countdown variable
        tk_countdown.set(f"The next update: {delay_sec} seconds")
        delay_sec -= 1  # Decrement the delay

        # Schedule the next update
        if delay_sec >= 0:
            window.after(1000, update_temperature_humidity)  # Schedule the next update after 1 second
        else:
            delay_progress_bar["value"] += 1
            tk_countdown.set(f"The next update: 0 seconds")  # Set countdown to 0 when the delay is complete
            delay_sec = old_delay_sec
            if not temperature == None:
                if allowtxt == 1:
                    info_xl.extend(write_to_txt(temperature,humidity,txt_filename))
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
                
            
            window.after(1000, update_temperature_humidity)
        if args.debug:
            tk_debug.set(f"Debug Window: {window.winfo_width()}x{window.winfo_height()} Box1: {frame_top_left.winfo_width()}x{frame_top_left.winfo_height()}\nBox2: {frame_top_right.winfo_width()}x{frame_top_right.winfo_height()} Box3: {frame_bottom_left.winfo_width()}x{frame_bottom_left.winfo_height()}\nBox4: {frame_bottom_right.winfo_width()}x{frame_bottom_right.winfo_height()}")
            
    
    except Exception as error:
        dhtDevice.exit()
        raise SystemExit(error)
    except KeyboardInterrupt:
        raise SystemExit

def update_graph():
    a.clear()
    if graph_show == "Temperature":
        a.plot(temperature_hold, label='Temperature')
    elif graph_show == "Humidity":
        a.plot(humidity_hold, label='Humidity')
    else:
        a.plot(temperature_hold, label='Temperature')
        a.plot(humidity_hold, label='Humidity')
    a.set_xlabel('Time')
    a.set_ylabel('Value')
    a.legend()
    canvas.draw()
    
def reset_values():
    temperature_hold.clear()
    humidity_hold.clear()
    insert_log_error(1,"Graph was reset")

def startup_reset_data():
    
    file_names = [txt_filename, "xl_tmp"]
    for file_name in file_names:
        try:
            os.remove(file_name)
            insert_log_error(1,f"File '{file_name}' deleted successfully")
        except FileNotFoundError:
            insert_log_error(2,"",f"File '{file_name}' not found")
        except PermissionError:
            insert_log_error(2,"",f"Unable to delete file '{file_name}'. Permission denied")
        except Exception as e:
            insert_log_error(2,"",f"An error occurred while deleting file '{file_name}': {str(e)}")    

window = tk.Tk()
window.title("DHT Reader " + version)

# Set the minimum size for the window (width, height)
window.minsize(800, 600)

# Define the layout using the grid geometry manager
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

# Create four subframes for the grids
frame_top_left = tk.Frame(master=window, bg=background_main)
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

graph_label = tk.Label(frame_top_right, text="Graph", bg=background_title, fg=foreground_main)
graph_label.pack(fill="x", padx=1)

fig = Figure(figsize=(5,4), dpi=100, facecolor=background_main)
a = fig.add_subplot(111)
a.set_xlabel('Time')
a.set_ylabel('Value')
a.tick_params(axis='x', colors=foreground_main)
a.tick_params(axis='y', colors=foreground_main)
a.spines['top'].set_color(foreground_main)
a.spines['bottom'].set_color(foreground_main)
a.spines['left'].set_color(foreground_main)
a.spines['right'].set_color(foreground_main)

a.set_facecolor(background_main)

# Create the legend and set its properties
legend = a.legend()

# Embed the figure in the Tkinter window
canvas = FigureCanvasTkAgg(fig, master=frame_top_right)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Add the navigation toolbar for basic interaction
toolbar = NavigationToolbar2Tk(canvas, frame_top_right)
toolbar.update()
toolbar.mode = "None"
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Create a Progressbar widget
delay_progress_bar = ttk.Progressbar(frame_top_right, orient="horizontal", mode="determinate")
delay_progress_bar.pack(fill="x", padx=20, pady=5)

# Subframe: Top Left (Information)
# Labels and Entry widgets

information_label = tk.Label(frame_top_left, text="Information", bg=background_title, fg=foreground_main)
information_label.pack(fill="x", padx=1)

device_label = tk.Label(frame_top_left, textvariable=tk_device, anchor="nw", bg=background_main, fg=foreground_main)
device_label.pack(fill="x")

pin_label = tk.Label(frame_top_left, textvariable=tk_pin, anchor="nw", bg=background_main,fg=foreground_main)
pin_label.pack(fill="x")

temperature_label = tk.Label(frame_top_left, textvariable=tk_temperature, anchor="nw", bg=background_main,fg=foreground_main)
temperature_label.pack(fill="x")

humidity_label = tk.Label(frame_top_left, textvariable=tk_humidity, anchor="nw", bg=background_main,fg=foreground_main)
humidity_label.pack(fill="x")

countdown_label = tk.Label(frame_top_left, textvariable=tk_countdown, anchor="nw", bg=background_main,fg=foreground_main)
countdown_label.pack(fill="x")

# Create a new frame to hold the button widgets
button_frame = tk.Frame(frame_top_left)
button_frame.pack(side="bottom",fill="x")

graph_reset_button = tk.Button(button_frame, text ="Reset graph", command = reset_values, bg=background_button, fg=foreground_main)
graph_reset_button.pack(fill="x",side="left")

settings_button = tk.Button(button_frame, text ="Settings", command = on_settings,bg=background_button, fg=foreground_main)
settings_button.pack(fill="x")

if args.debug:
    tk_debug = tk.StringVar(window)
    debug_label = tk.Label(frame_top_left, textvariable=tk_debug, anchor="sw", bg=background_main)
    debug_label.pack(side="bottom",fill="x")
# Subframe: Bottom Left (Logs)
# Labels and Entry widgets
logs_label = tk.Label(frame_bottom_left, text="Logs", bg=background_title, fg=foreground_main)
logs_label.pack(fill="x")

# Create a Listbox widget
logs_listbox = tk.Listbox(frame_bottom_left, selectmode=tk.SINGLE,  bg=background_errors_logs, fg = foreground_logs)

# Create a Scrollbar widget
logs_scrollbar = tk.Scrollbar(frame_bottom_left, command=logs_listbox.yview)

# Configure the Listbox to use the Scrollbar
logs_listbox.config(yscrollcommand=logs_scrollbar.set)

logs_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Subframe: Bottom Right (Errors)

# Labels and Entry widgets
errors_label = tk.Label(frame_bottom_right, text="Errors", bg=background_title, fg=foreground_main)
errors_label.pack(fill="x",padx=1)

# Create a Listbox widget
errors_listbox = tk.Listbox(frame_bottom_right, selectmode=tk.SINGLE, bg=background_errors_logs, fg = foreground_errors)

# Create a Scrollbar widget
errors_scrollbar = tk.Scrollbar(frame_bottom_right, command=errors_listbox.yview)

# Configure the Listbox to use the Scrollbar
errors_listbox.config(yscrollcommand=errors_scrollbar.set)

errors_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
errors_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

if args.autodetect:
    auto_detect(0,0)

if args.debug:
    insert_log_error(1,"Debug mode activated with --debug")
if reset_data == 1:
    startup_reset_data()

window.protocol("WM_DELETE_WINDOW", on_close)

update_graph()
window.after(1000, update_temperature_humidity)

window.mainloop()
