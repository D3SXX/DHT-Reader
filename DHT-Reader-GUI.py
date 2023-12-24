#DHT Reader v0.3 hotfix 2 by D3SXX

try:
    import os
    import time
    from datetime import datetime
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
    from Core import config
    from Core import device
    from Core import output
    from Core import get_time
except Exception as e:
    raise SystemExit(f"Some dependencies are missing. Please run the following command to install them:\npip3 install adafruit_blinka adafruit-circuitpython-dht matplotlib xlsxwriter\n{e}")


version = "v0.4d Beta"
        
class Theme:
    def __init__(self):
        self.background_main = "white"
        self.background_errors_logs = "white"
        self.background_title = "lightgray"
        self.background_button = "lightgray"
        self.foreground_main = "black"
        self.foreground_logs = "black"
        self.foreground_errors = "red"
    def change(self, theme):
        if theme == "default-black":
            self.background_main = "black"
            self.background_errors_logs = "black"
            self.background_title = "gray"
            self.background_button = "#3d3d5c"
            self.foreground_main = "white"
            self.foreground_logs = "white"
            self.foreground_errors = "red"
        elif theme == "classic-white":
            self.background_main = "black"
            self.background_errors_logs = "black"
            self.background_title = "purple"
            self.background_button = "#3d3d5c"
            self.foreground_main = "white"
            self.foreground_logs = "white"
            self.foreground_errors = "red"
        elif theme == "classic-blue":
            self.background_main = "blue"
            self.background_errors_logs = "blue"
            self.background_title = "gray"
            self.background_button = "#3d3d5c"
            self.foreground_main = "white"
            self.foreground_logs = "white"
            self.foreground_errors = "red"
        else:
            self.background_main = "white"
            self.background_errors_logs = "white"
            self.background_title = "lightgray"
            self.background_button = "lightgray"
            self.foreground_main = "black"
            self.foreground_logs = "black"
            self.foreground_errors = "red"                    
    

def insert_log_error(flag, log_msg = "", error_msg = ""):
    """
    Insert log or/and error string to appropriate GUI box
    
    If debug is active also prints message(s) to console
    
    Args:
        flag (int): 1 for log, 2 for error, 3 for both error and log
        log_msg (string): String for log message. Defaults to "".
        error_msg (string): String for error message. Defaults to "".
    """
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


def auto_detect():

    def update_gui_logs(msg, value=None):
        if program_data.tmp_enable_gui:
            autodetect_listbox.insert(tk.END, msg)
            autodetect_listbox.see(tk.END)
            if value:
                progress_bar["value"] = program_data.tmp_max_value
            else:
                progress_bar["value"] += 1 
    global dht_device, after_id
    if program_data.tmp_enable_gui and not program_data.tmp_device_model:
        if program_data.tmp_last_pin >= 7 and program_data.tmp_last_pin < 8:
            cut_val = 6
        elif program_data.tmp_last_pin >= 8:
            cut_val = 12
        else:
            cut_val = 0
        if program_data.tmp_first_pin > 0:
            val = program_data.tmp_first_pin
        else:
            val = 0
        program_data.tmp_max_value = (program_data.tmp_last_pin+1-program_data.tmp_first_pin)*3*2-cut_val+val
        progress_bar["value"] = program_data.tmp_first_pin
        progress_bar["maximum"] = program_data.tmp_max_value
        
    if program_data.tmp_device_model is None:
        program_data.tmp_pulseio = True
        program_data.tmp_device_model = program_data.devices[program_data.devices.index(program_data.tmp_device_model)+1]
        program_data.tmp_found_device = False
        program_data.tmp_pin = program_data.tmp_first_pin
    if program_data.tmp_pin == program_data.tmp_last_pin:
        print( program_data.devices.index(program_data.tmp_device_model),len(program_data.devices)-1)
        if program_data.devices.index(program_data.tmp_device_model) < len(program_data.devices)-1:
            program_data.tmp_pin = program_data.tmp_first_pin
            if program_data.tmp_pulseio:
                program_data.tmp_pulseio = False
                msg = f"Pulseio is set to {program_data.tmp_pulseio}"
                print(msg)
                update_gui_logs(msg)
            else:
                program_data.tmp_pulseio = True
                program_data.tmp_device_model = program_data.devices[program_data.devices.index(program_data.tmp_device_model)+1]
            msg = f"Checking the {program_data.tmp_device_model}"
            print(msg)
            update_gui_logs(msg)
        else:
            return
    else:
        program_data.tmp_pin += 1

    try:
        if program_data.tmp_pin == 7 or program_data.tmp_pin == 8:
            after_id = autodetect_window.after(50,auto_detect)
            return
        dht_device = device.re_init(None,dht_device, program_data.tmp_device_model, program_data.tmp_pin, program_data.tmp_pulseio)
        msg = f"Checking pin {program_data.tmp_pin}"
        print(msg)
        update_gui_logs(msg)
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        print(temperature,humidity)
        msg = f"Detected {program_data.tmp_device_model} at pin {program_data.tmp_pin} (Pulseio is set to {program_data.tmp_pulseio})"
        program_data.tmp_found_device = True
        update_gui_logs(msg,program_data.tmp_scan_all_pins)
        print(msg)
        if program_data.tmp_enable_gui:
            tk_device.set(f"Device: {program_data.tmp_device_model}")
            tk_pin.set(f"Pin: {program_data.tmp_pin}")
    except RuntimeError as error:
        if str(error) == "DHT sensor not found, check wiring":
            print(f"Error: {error}")                
        else:
            print(error)
            msg = f"Detected {program_data.tmp_device_model} at pin {program_data.tmp_pin} (Pulseio is set to {program_data.tmp_pulseio})"
            program_data.tmp_found_device = True
            update_gui_logs(msg,True)
            print(msg)
            if program_data.tmp_enable_gui:
                tk_device.set(f"Device: {program_data.tmp_device_model}")
                tk_pin.set(f"Pin: {program_data.tmp_pin}")
    if not program_data.tmp_scan_all_pins and program_data.tmp_found_device:
        return
    else:
        after_id = autodetect_window.after(50,auto_detect)

       
                #autodetect_listbox.insert(tk.END, msg)
                #autodetect_listbox.see(tk.END)
                #autodetect_listbox.update_idletasks()

# Array for holding temperature and humidity
temperature_hold = []
humidity_hold = []
info_xl = []



parser = argparse.ArgumentParser(description='A DHT-Reader CLI Interface')
parser.add_argument('--skip', action='store_true', help='Skip config check')
parser.add_argument('--debug', action='store_true', help='Show debug info')
parser.add_argument('--autodetect', action='store_true', help='Auto detect device')
args = parser.parse_args()
data = config.Data()
program_data = config.ProgramData()
theme = Theme()

if not args.skip:
    if config.check():
        config.read(data)
    else:
        config.create(data)

global dht_device
dht_device = device.init(data)

theme.change(data.select_theme)

old_delay_sec = data.delay_sec
delay_sec = old_delay_sec

def on_autodetect():
    def change_scan_all():
        program_data.tmp_scan_all_pins = not program_data.tmp_scan_all_pins
        if args.debug:
            insert_log_error(1, f"scan_all is set to {program_data.tmp_scan_all_pins}")

    def on_enter_first_pin(event):
        program_data.tmp_first_pin = int(first_pin_entry.get())
        if args.debug:
            insert_log_error(1, f"first_pin is set to {program_data.tmp_first_pin}")

    def on_enter_last_pin(event):
        program_data.tmp_last_pin = int(last_pin_entry.get())
        if args.debug:
            insert_log_error(1, f"last_pin is set to {program_data.tmp_last_pin}")

    def on_start():
        program_data.tmp_device_model = None
        auto_detect()

    def on_stop():
        global after_id
        if after_id:
            autodetect_window.after_cancel(after_id)
            after_id = None

    global autodetect_listbox, progress_bar, scan_all, first_pin, last_pin,autodetect_window

    first_pin = 0
    last_pin = 20
    s = ttk.Style()
    s.configure("Custom.TLabelframe", background=theme.background_main)

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
    
    controls_frame = ttk.LabelFrame(window_frame, text="Controls", padding=5, style="Custom.TLabelframe")
    controls_frame.grid(row=0, column=0, sticky="ew")
    autodetect_frame_button = ttk.Button(controls_frame, text="Detect Device", command=on_start, style="Custom.TButton")
    autodetect_frame_button.grid(row=0, column=0,sticky="nsew")
    stop_frame_button = ttk.Button(controls_frame, text="Stop", command=on_stop, style="Custom.TButton")
    stop_frame_button.grid(row=0, column=1,sticky="nsew")    
    scan_all_checkbox = tk.Checkbutton(controls_frame, text="Don't stop scanning",command=change_scan_all)
    scan_all_checkbox.grid(row=1, column=0)
    
    if program_data.tmp_scan_all_pins:
        scan_all_checkbox.state(['selected'])
    program_data.tmp_enable_gui = True
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
    autodetect_listbox = tk.Listbox(window_frame, selectmode=tk.SINGLE, bg=theme.background_errors_logs, fg=theme.foreground_logs)
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
        data.device_model = option_var.get()
        tk_device.set(f"Device: {data.device_model}")
        insert_log_error(1,f"Device was changed to {data.device_model}")
        global dht_device
        dht_device = device.re_init(data,dht_device)
    
    def on_pin_entry_return(event):
        data.pin = pin_entry_var.get()
        tk_pin.set(f"Pin: {data.pin}")
        insert_log_error(1,f"Pin was changed to {data.pin}")
        global dht_device
        dht_device = device.re_init(data, dht_device)
    
    def on_checkbox_change(option):
        if option == 0:
            data.allow_txt = not data.allow_txt
            insert_log_error(1,f"Writing to a txt file is set to {data.allow_txt}")

        elif option == 1:
            data.allow_xl = not data.allow_xl
            insert_log_error(1,f"Writing to a Excel file is set to {data.allow_xl}")
        elif option == 2:
            data.allow_img = not data.allow_img
            insert_log_error(1,f"Writing to an Image file is set to {data.allow_img}")
        elif option == 3:
            data.allow_pulseio = not data.allow_pulseio
            insert_log_error(1,f"Using Pulseio is set to {data.allow_pulseio}")
            global dht_device
            dht_device = device.re_init(data, dht_device) 
        elif option == 4:
            data.reset_data = not data.reset_data
            insert_log_error(1,f"Reset data at startup is set to {data.reset_data}")
            
    def on_filename_entry_return(option, value):
        if option == 0:
            data.txt_filename = value.get()
            print(f"New txt filename: {data.txt_filename}")
            insert_log_error(1,f"Text filename was changed to {data.txt_filename}")
        elif option == 1:
            data.xl_filename = value.get()
            print(f"New Excel filename: {data.xl_filename}")
            insert_log_error(1,f"Excel filename was changed to {data.xl_filename}")
        elif option == 2:
            data.img_filename = value.get()
            print(f"New image filename: {data.img_filename}")
            insert_log_error(1,f"Image filename was changed to {data.img_filename}")
    
    def change_temperature_unit(unit):
        if unit == "C":
            c_unit_button.config(relief=tk.SUNKEN)
            f_unit_button.config(relief=tk.RAISED)
        elif unit == "F":
            c_unit_button.config(relief=tk.RAISED)
            f_unit_button.config(relief=tk.SUNKEN)
        data.temperature_unit = unit
        insert_log_error(1,f"Temperature unit was changed to °{unit}")
            
    def change_graph(option):
        if option == "T":
            data.graph_show = "Temperature"
            T_graph_change_button.config(relief=tk.SUNKEN)
            T_H_graph_change_button.config(relief=tk.RAISED)
            H_graph_change_button.config(relief=tk.RAISED)
            insert_log_error(1,f"Graph now shows only {data.graph_show}")
        elif option == "H":
            data.graph_show = "Humidity"
            T_graph_change_button.config(relief=tk.RAISED)
            T_H_graph_change_button.config(relief=tk.RAISED)
            H_graph_change_button.config(relief=tk.SUNKEN)
            insert_log_error(1,f"Graph now shows only {data.graph_show}")
        else:
            data.graph_show = "Both"
            T_graph_change_button.config(relief=tk.RAISED)
            T_H_graph_change_button.config(relief=tk.SUNKEN)
            H_graph_change_button.config(relief=tk.RAISED)
            insert_log_error(1,f"Graph now shows both temperature and humidity")

    def on_change_delay(value, flag = 0):
        if flag == 1:
            value = value.get()
        if value > 0:
            data.delay_sec = value
            delay_entry_var.set(data.delay_sec)
            delay_decrease_button.config(relief=tk.RAISED)
            insert_log_error(1,f"Delay was changes to {data.delay_sec} second(s)")
            if value == 1:
                delay_decrease_button.config(relief=tk.SUNKEN)
        else:
            delay_decrease_button.config(relief=tk.SUNKEN)
            if args.debug:
                insert_log_error(1,f"debug: delay value is too small to decrease --> {data.delay_sec}")

    def on_theme_select(select):
        data.select_theme  = select
        insert_log_error(1,f"Theme selected: {select}")
        
    def on_select(event):
        
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
                    insert_log_error(1,f"Menu options: {device_options} current device: {data.device_model}")
                    insert_log_error(1,f"Current pin: {data.pin}")
                    insert_log_error(1,f"pulseio: {data.allow_pulseio}")
                if data.device_model == "DHT11": # Set the default option (depends on the current device)
                    option_var.set(device_options[0])
                elif data.device_model == "DHT21":
                    option_var.set(device_options[1])  
                elif data.device_model == "DHT22":
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
                pin_entry_var.set(data.pin)  # Set the default value to the current variable
                pin_entry = tk.Entry(entry_frame, textvariable=pin_entry_var,bg=theme.background_main, fg=theme.foreground_main)
                pin_entry.pack(anchor="w")
                
                # Bind the "Return" key event to the Entry widget
                pin_entry.bind("<Return>", on_pin_entry_return)        
                
                # Optional
                
                # Create a new frame to hold the optional widgets
                optional_frame = ttk.LabelFrame(main_frame, text="Optional", padding=5)
                optional_frame.pack(anchor="nw")
                
                checkbox_allowpulseio_var = tk.BooleanVar(value=data.allow_pulseio)
                
                allowpulseio_checkbox = tk.Checkbutton(optional_frame, text="Enable Pulseio", variable=checkbox_allowpulseio_var, command=lambda: on_checkbox_change(3))
                allowpulseio_checkbox.pack(anchor="nw")
                if data.allow_pulseio:
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
                    insert_log_error(1,f"allow_txt: {data.allow_txt}")
                    insert_log_error(1,f"allow_xl: {data.allow_xl}")
                    insert_log_error(1,f"allow_img: {data.allow_img}")
                    insert_log_error(1,f"txt_filename: {data.txt_filename}")
                    insert_log_error(1,f"excel_filename: {data.xl_filename}")
                    insert_log_error(1,f"img_filename: {data.img_filename}")
                    insert_log_error(1,f"reset_data: {data.reset_data}")
                    
                # Create a new frame to hold the checkbutton widgets
                checkbutton_frame = ttk.LabelFrame(data_frame, text="Save data to formats:", padding=5)
                checkbutton_frame.pack(anchor="nw")

                allowtxt_checkbox = tk.Checkbutton(checkbutton_frame, text="txt file",command=lambda: on_checkbox_change(0))
                allowtxt_checkbox.pack(anchor="w")
                if data.allow_txt:
                    allowtxt_checkbox.select()
                
                allowxl_checkbox = tk.Checkbutton(checkbutton_frame, text="Excel file",command=lambda: on_checkbox_change(1))
                allowxl_checkbox.pack(anchor="w")
                if data.allow_xl:
                    allowxl_checkbox.select()
                
                allowimg_checkbox = tk.Checkbutton(checkbutton_frame, text="Image file",command=lambda: on_checkbox_change(2))
                allowimg_checkbox.pack(anchor="w")
                if data.allow_img:
                    allowimg_checkbox.select()
                
                # Create a new frame to hold the Entry widgets
                entry_frame = ttk.LabelFrame(data_frame, text="Change filenames", padding=5)
                entry_frame.pack(anchor="nw")          
                
                # Change filename for txt
                txt_filename_label = ttk.Label(entry_frame, text="Current txt filename: ")
                txt_filename_label.pack(anchor="w")
                
                # txt Entry
                txt_filename_entry_var = tk.StringVar(entry_frame)
                txt_filename_entry_var.set(data.txt_filename)  # Set the default value to the current variable
                txt_filename_entry = tk.Entry(entry_frame, textvariable=txt_filename_entry_var, bg=theme.background_main, fg=theme.foreground_main)
                txt_filename_entry.pack(anchor="w")
                
                # Bind the "Return" key event to the Entry widget
                txt_filename_entry.bind("<Return>", lambda event: on_filename_entry_return(0, txt_filename_entry_var))   
                
                # Change filename for Excel
                excel_filename_label = tk.Label(entry_frame, text="Current Excel filename: ")
                excel_filename_label.pack(anchor="w")
                
                # excel Entry
                excel_filename_entry_var = tk.StringVar(entry_frame)
                excel_filename_entry_var.set(data.xl_filename)  # Set the default value to the current variable
                excel_filename_entry = tk.Entry(entry_frame, textvariable=excel_filename_entry_var, bg=theme.background_main, fg=theme.foreground_main)
                excel_filename_entry.pack(anchor="w")
                
                # Bind the "Return" key event to the Entry widget
                excel_filename_entry.bind("<Return>", lambda event: on_filename_entry_return(1, excel_filename_entry_var))
                
                # Change filename for Image
                img_filename_label = ttk.Label(entry_frame, text="Current Image filename: ")
                img_filename_label.pack(anchor="w")
                
                # excel Entry
                img_filename_entry_var = tk.StringVar(entry_frame)
                img_filename_entry_var.set(data.img_filename)  # Set the default value to the current variable
                img_filename_entry = tk.Entry(entry_frame, textvariable=img_filename_entry_var, bg=theme.background_main, fg=theme.foreground_main)
                img_filename_entry.pack(anchor="w")
                
                # Bind the "Return" key event to the Entry widget
                img_filename_entry.bind("<Return>", lambda event: on_filename_entry_return(2, img_filename_entry_var))    
                
                # Create a new frame to hold the optional widgets
                optional_frame = ttk.LabelFrame(data_frame, text="Optional", padding=5)
                optional_frame.pack(anchor="nw")
                
                reset_data_var = tk.BooleanVar()
                
                reset_data_checkbox = tk.Checkbutton(optional_frame,variable=reset_data_var, text="Reset data at startup",command=lambda: on_checkbox_change(4))
                reset_data_checkbox.pack(anchor="w")
                if data.reset_data:
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
                    insert_log_error(1,f"temperature_unit: {data.temperature_unit}")
                    insert_log_error(1,f"graph_show: {data.graph_show}")
                    insert_log_error(1,f"delay_sec: {data.delay_sec}")
                    insert_log_error(1,f"select_theme: {data.select_theme}")
                
                # Change temperature unit
                temperature_unit_frame = ttk.LabelFrame(general_frame, text="Change temperature unit", padding=5)
                temperature_unit_frame.pack(anchor="nw")
                # Create a new frame to hold the temperature unit change widgets
                
                temperature_unit_label = ttk.Label(temperature_unit_frame, text="Unit: ")
                temperature_unit_label.pack(side="left")
                
                c_unit_button = tk.Button(temperature_unit_frame, text ="°C", command = lambda: change_temperature_unit("C"), bg=theme.background_button, fg=theme.foreground_main)
                c_unit_button.pack(side="left")
                f_unit_button = tk.Button(temperature_unit_frame, text ="°F", command = lambda: change_temperature_unit("F"), bg=theme.background_button, fg=theme.foreground_main)
                f_unit_button.pack(side="left")
                
                # Set the initial relief of the buttons based on the current temperature_unit
                c_unit_button.config(relief=tk.SUNKEN if data.temperature_unit == "C" else tk.RAISED)
                f_unit_button.config(relief=tk.SUNKEN if data.temperature_unit == "F" else tk.RAISED)
                
                graph_change_frame = ttk.LabelFrame(general_frame, text="Change graph", padding=5)
                graph_change_frame.pack(anchor="nw")
                
                T_graph_change_button = tk.Button(graph_change_frame, text ="Only Temperature", command = lambda: change_graph("T"), bg=theme.background_button, fg=theme.foreground_main)
                T_graph_change_button.pack(side="left")
                T_H_graph_change_button = tk.Button(graph_change_frame, text ="Both", command = lambda: change_graph("Both"), bg=theme.background_button, fg=theme.foreground_main)
                T_H_graph_change_button.pack(side="left")
                H_graph_change_button = tk.Button(graph_change_frame, text ="Only Humidity", command = lambda: change_graph("H"), bg=theme.background_button, fg=theme.foreground_main)
                H_graph_change_button.pack(side="left")
                
                # Set the initial relief of the buttons based on the current graph_show
                T_graph_change_button.config(relief=tk.SUNKEN if data.graph_show == "Temperature" else tk.RAISED)
                T_H_graph_change_button.config(relief=tk.SUNKEN if data.graph_show == "Both" else tk.RAISED)
                H_graph_change_button.config(relief=tk.SUNKEN if data.graph_show == "Humidity" else tk.RAISED)
                
                delay_change_frame = ttk.LabelFrame(general_frame, text="Change delay", padding=5)
                delay_change_frame.pack(anchor="nw")
                
                delay_decrease_button = tk.Button(delay_change_frame, text ="-", command = lambda: on_change_delay(data.delay_sec-1),bg=theme.background_button, fg=theme.foreground_main)
                delay_decrease_button.pack(side="left")
                
                # delay Entry
                delay_entry_var = tk.IntVar(delay_change_frame)
                delay_entry_var.set(data.delay_sec)  # Set the default value to the current variable
                delay_change_entry = tk.Entry(delay_change_frame, textvariable=delay_entry_var,bg=theme.background_main, fg=theme.foreground_main)
                delay_change_entry.pack(side="left")
                
                # Bind the "Return" key event to the Entry widget
                delay_change_entry.bind("<Return>", lambda event: on_change_delay(delay_entry_var,1))   
                
                delay_increase_button = tk.Button(delay_change_frame, text ="+", command = lambda: on_change_delay(data.delay_sec+1),bg=theme.background_button, fg=theme.foreground_main)
                delay_increase_button.pack(side="left")
                
                # Create a new frame to hold the theme change widgets
                theme_change_frame = ttk.LabelFrame(general_frame, text="Change theme", padding=5)
                theme_change_frame.pack(anchor="nw")
                                
                themes_options = ["default-white", "default-black", "classic-black", "classic-blue"]
                option_var = tk.StringVar(theme_change_frame)
                option_var.set(data.select_theme) 
                    
                theme_label = ttk.Label(theme_change_frame, text="Current theme: ")
                theme_label.pack(side="left")
                      
                option_menu = tk.OptionMenu(theme_change_frame,option_var,*themes_options,command=lambda selected_value: on_theme_select(selected_value))

                option_menu.pack(fill="x", anchor="w")
                
                # Set the initial relief of the buttons based on the current graph_show
                delay_decrease_button.config(relief=tk.SUNKEN if data.delay_sec <= 1 else tk.RAISED)
                
            selected_item = listbox.get(selected_index)

    def on_close_settings():
        settings_window.destroy()
        config.create(data)
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
    frame_left = tk.Frame(master=settings_window, bg=theme.background_main)
    frame_right = tk.Frame(master=settings_window, bg=theme.background_main)

    # Grid layout for the four subframes
    frame_left.grid(row=0, column=0, sticky="nsew")
    frame_right.grid(row=0, column=1,sticky="nsew", padx = 2, pady = 10)

    # Listbox container
    listbox_container = tk.Frame(master=frame_left)
    listbox_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Create a Listbox with some options
    options = [f"Device & Pin", f"Data Save & Reset", "General"]
    listbox = tk.Listbox(listbox_container, selectmode=tk.SINGLE, bg=theme.background_main, fg=theme.foreground_main)
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
    device.stop(dht_device)
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
            start_time = get_time.time_s()
            temperature, humidity = device.get_data(dht_device)
            if not temperature:
                insert_log_error(3,f"Error happened at {get_time.date()}, retrying in 1 sec",humidity)
                # Try to do a scan in a second
                window.after(1000, update_temperature_humidity)
                return    
            time_took = get_time.time_s() - start_time
            if args.debug:
                print(f"Took {time_took} to scan")
            if data.temperature_unit == "F":
                temperature = int(1.8 * temperature + 32)
            temperature_hold.append(temperature)
            humidity_hold.append(humidity)
            update_graph()
            

        # Update tk values
        tk_temperature.set(f"Temperature: {temperature} °{data.temperature_unit}")
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
                if data.allow_txt:
                    info_xl.extend(output.txt(temperature, humidity, data.txt_filename))
                if data.allow_xl:
                    info_xl.extend(output.xl(temperature, humidity, data.xl_filename,program_data.tmp_folderpath,program_data.xl_tmp_filename))
                if data.allow_img:
                    info_xl.extend(output.img(temperature, humidity, data.img_filename,program_data.tmp_folderpath, program_data.img_tmp_filename))
                
            
            window.after(1000, update_temperature_humidity)
        if args.debug:
            tk_debug.set(f"Debug Window: {window.winfo_width()}x{window.winfo_height()} Box1: {frame_top_left.winfo_width()}x{frame_top_left.winfo_height()}\nBox2: {frame_top_right.winfo_width()}x{frame_top_right.winfo_height()} Box3: {frame_bottom_left.winfo_width()}x{frame_bottom_left.winfo_height()}\nBox4: {frame_bottom_right.winfo_width()}x{frame_bottom_right.winfo_height()}")
            
    
    except Exception as error:
        device.stop(dht_device)
        raise SystemExit(error)
    except KeyboardInterrupt:
        device.stop(dht_device)
        raise SystemExit

def update_graph():
    a.clear()
    if data.graph_show == "Temperature":
        a.plot(temperature_hold, label='Temperature')
    elif data.graph_show == "Humidity":
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


window = tk.Tk()
window.title("DHT Reader " + version)

# Set the minimum size for the window (width, height)
window.minsize(800, 600)

# Define the layout using the grid geometry manager
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

# Create four subframes for the grids
frame_top_left = tk.Frame(master=window, bg=theme.background_main)
frame_top_right = tk.Frame(master=window, bg="white")
frame_bottom_left = tk.Frame(master=window, bg="white")
frame_bottom_right = tk.Frame(master=window, bg="white")

# Grid layout for the four subframes
frame_top_left.grid(row=0, column=0, sticky="nsew")
frame_top_right.grid(row=0, column=1, sticky="nsew")
frame_bottom_left.grid(row=1, column=0, sticky="nsew")
frame_bottom_right.grid(row=1, column=1, sticky="nsew")

# Variables to store values in information box

tk_device = tk.StringVar(window, f"Device: {data.device_model}")
tk_pin = tk.StringVar(window, f"Pin: {data.pin}")
tk_temperature = tk.StringVar(window, "Temperature: ")
tk_humidity = tk.StringVar(window, "Humidity: ")
tk_countdown = tk.StringVar()
tk_countdown.set(f"{data.delay_sec} seconds")
tk_logs = tk.StringVar(window)
tk_errors = tk.StringVar(window)

# Graph box
frame_graph = tk.Frame(master=window)
frame_graph.grid(row=0, column=1, rowspan=3, padx=1, pady=1)

# Create the GUI elements and layout for each subframe
# Subframe: Top Right (Graph)
# Create the figure and axis for the interactive graph

graph_label = tk.Label(frame_top_right, text="Graph", bg=theme.background_title, fg=theme.foreground_main)
graph_label.pack(fill="x", padx=1)

fig = Figure(figsize=(5,4), dpi=100, facecolor=theme.background_main)
a = fig.add_subplot(111)
a.set_xlabel('Time')
a.set_ylabel('Value')
a.tick_params(axis='x', colors=theme.foreground_main)
a.tick_params(axis='y', colors=theme.foreground_main)
a.spines['top'].set_color(theme.foreground_main)
a.spines['bottom'].set_color(theme.foreground_main)
a.spines['left'].set_color(theme.foreground_main)
a.spines['right'].set_color(theme.foreground_main)

a.set_facecolor(theme.background_main)

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

information_label = tk.Label(frame_top_left, text="Information", bg=theme.background_title, fg=theme.foreground_main)
information_label.pack(fill="x", padx=1)

device_label = tk.Label(frame_top_left, textvariable=tk_device, anchor="nw", bg=theme.background_main, fg=theme.foreground_main)
device_label.pack(fill="x")

pin_label = tk.Label(frame_top_left, textvariable=tk_pin, anchor="nw", bg=theme.background_main,fg=theme.foreground_main)
pin_label.pack(fill="x")

temperature_label = tk.Label(frame_top_left, textvariable=tk_temperature, anchor="nw", bg=theme.background_main,fg=theme.foreground_main)
temperature_label.pack(fill="x")

humidity_label = tk.Label(frame_top_left, textvariable=tk_humidity, anchor="nw", bg=theme.background_main,fg=theme.foreground_main)
humidity_label.pack(fill="x")

countdown_label = tk.Label(frame_top_left, textvariable=tk_countdown, anchor="nw", bg=theme.background_main,fg=theme.foreground_main)
countdown_label.pack(fill="x")

# Create a new frame to hold the button widgets
button_frame = tk.Frame(frame_top_left)
button_frame.pack(side="bottom",fill="x")

graph_reset_button = tk.Button(button_frame, text ="Reset graph", command = reset_values, bg=theme.background_button, fg=theme.foreground_main)
graph_reset_button.pack(fill="x",side="left")

settings_button = tk.Button(button_frame, text ="Settings", command = on_settings,bg=theme.background_button, fg=theme.foreground_main)
settings_button.pack(fill="x")

if args.debug:
    tk_debug = tk.StringVar(window)
    debug_label = tk.Label(frame_top_left, textvariable=tk_debug, anchor="sw", bg=theme.background_main)
    debug_label.pack(side="bottom",fill="x")
# Subframe: Bottom Left (Logs)
# Labels and Entry widgets
logs_label = tk.Label(frame_bottom_left, text="Logs", bg=theme.background_title, fg=theme.foreground_main)
logs_label.pack(fill="x")

# Create a Listbox widget
logs_listbox = tk.Listbox(frame_bottom_left, selectmode=tk.SINGLE,  bg=theme.background_errors_logs, fg = theme.foreground_logs)

# Create a Scrollbar widget
logs_scrollbar = tk.Scrollbar(frame_bottom_left, command=logs_listbox.yview)

# Configure the Listbox to use the Scrollbar
logs_listbox.config(yscrollcommand=logs_scrollbar.set)

logs_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Subframe: Bottom Right (Errors)

# Labels and Entry widgets
errors_label = tk.Label(frame_bottom_right, text="Errors", bg=theme.background_title, fg=theme.foreground_main)
errors_label.pack(fill="x",padx=1)

# Create a Listbox widget
errors_listbox = tk.Listbox(frame_bottom_right, selectmode=tk.SINGLE, bg=theme.background_errors_logs, fg = theme.foreground_errors)

# Create a Scrollbar widget
errors_scrollbar = tk.Scrollbar(frame_bottom_right, command=errors_listbox.yview)

# Configure the Listbox to use the Scrollbar
errors_listbox.config(yscrollcommand=errors_scrollbar.set)

errors_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
errors_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

if args.autodetect:
    auto_detect()

if args.debug:
    insert_log_error(1,"Debug mode activated with --debug")
if data.reset_data:
    output.startup_reset_data(data,program_data)

window.protocol("WM_DELETE_WINDOW", on_close)

update_graph()
window.after(1000, update_temperature_humidity)

window.mainloop()
